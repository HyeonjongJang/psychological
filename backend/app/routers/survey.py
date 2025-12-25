"""G1: Traditional Survey API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..core.database import get_db
from ..core.mini_ipip6_data import MINI_IPIP6_ITEMS, SURVEY_ORDER
from ..models import (
    Participant, AssessmentSession, SessionType, SessionStatus,
    ItemResponse, AssessmentResult
)
from ..schemas import (
    SurveyItem, SurveyItemsResponse, SurveySubmit, SessionResponse
)
from ..services.scoring_service import calculate_all_trait_scores, validate_complete_responses
from ..services.counterbalancing import get_sequence_number

router = APIRouter()


@router.post("/{participant_id}/start", response_model=SessionResponse)
async def start_survey(
    participant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Start a new survey session for a participant."""
    # Verify participant exists
    result = await db.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    # Check if survey already completed
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.session_type == SessionType.SURVEY)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey already completed for this participant"
        )

    # Get sequence number
    sequence = get_sequence_number(participant.condition_order, "survey")

    # Create new session
    session = AssessmentSession(
        participant_id=participant_id,
        session_type=SessionType.SURVEY,
        sequence_number=sequence,
        status=SessionStatus.IN_PROGRESS,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


@router.get("/{session_id}/items", response_model=SurveyItemsResponse)
async def get_survey_items(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all survey items for a session."""
    # Verify session exists and is survey type
    result = await db.execute(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.session_type != SessionType.SURVEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not a survey type"
        )

    # Build items list
    items = [
        SurveyItem(
            item_number=num,
            text=MINI_IPIP6_ITEMS[num]["text"],
            trait=MINI_IPIP6_ITEMS[num]["trait"],
        )
        for num in SURVEY_ORDER
    ]

    return SurveyItemsResponse(
        session_id=session_id,
        items=items,
        total_items=24,
    )


@router.post("/{session_id}/submit")
async def submit_survey(
    session_id: str,
    data: SurveySubmit,
    db: AsyncSession = Depends(get_db)
):
    """Submit all survey responses and complete the session."""
    # Verify session exists
    result = await db.execute(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.session_type != SessionType.SURVEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not a survey type"
        )

    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed"
        )

    # Convert responses to dict and validate
    responses_dict = {r.item_number: r.value for r in data.responses}
    validation = validate_complete_responses(responses_dict)

    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid responses: missing={validation['missing_items']}, invalid={validation['invalid_values']}"
        )

    # Save all responses
    for idx, response_data in enumerate(data.responses):
        item = MINI_IPIP6_ITEMS[response_data.item_number]
        response = ItemResponse(
            session_id=session_id,
            item_number=response_data.item_number,
            trait=item["trait"],
            response_value=response_data.value,
            presentation_order=idx + 1,
        )
        db.add(response)

    # Calculate scores
    scores = calculate_all_trait_scores(responses_dict)

    # Calculate duration
    duration = int((datetime.utcnow() - session.started_at).total_seconds())

    # Create result
    result_obj = AssessmentResult(
        session_id=session_id,
        extraversion_score=scores["extraversion"]["score"],
        agreeableness_score=scores["agreeableness"]["score"],
        conscientiousness_score=scores["conscientiousness"]["score"],
        neuroticism_score=scores["neuroticism"]["score"],
        openness_score=scores["openness"]["score"],
        honesty_humility_score=scores["honesty_humility"]["score"],
        total_items_administered=24,
        total_duration_seconds=duration,
    )
    db.add(result_obj)

    # Update session status
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.utcnow()
    session.duration_seconds = duration
    session.items_administered = 24

    await db.commit()
    await db.refresh(result_obj)

    return {
        "session_id": session_id,
        "status": "completed",
        "scores": {
            trait: {"score": data["score"], "num_items": data["num_items"]}
            for trait, data in scores.items()
        },
        "duration_seconds": duration,
    }
