"""G2: Static Chatbot API endpoints."""
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
    StaticStartResponse, StaticRespond, StaticRespondResponse, SessionResponse
)
from ..services.scoring_service import calculate_all_scores_from_list
from ..services.counterbalancing import get_sequence_number

router = APIRouter()


@router.post("/{participant_id}/start", response_model=StaticStartResponse)
async def start_static_chatbot(
    participant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Start a new static chatbot session."""
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

    # Check if static chatbot already completed
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.session_type == SessionType.STATIC)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Static chatbot already completed for this participant"
        )

    # Get sequence number
    sequence = get_sequence_number(participant.condition_order, "static")

    # Create new session
    session = AssessmentSession(
        participant_id=participant_id,
        session_type=SessionType.STATIC,
        sequence_number=sequence,
        status=SessionStatus.IN_PROGRESS,
        items_administered=0,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Get first item
    first_item_num = SURVEY_ORDER[0]
    first_item = MINI_IPIP6_ITEMS[first_item_num]

    return StaticStartResponse(
        session_id=session.id,
        message="Hi! I'm going to ask you some questions about yourself. Please rate how accurately each statement describes you on a scale from 1 (Very Inaccurate) to 7 (Very Accurate).",
        current_item=1,
        item_text=first_item["text"],
        total_items=24,
    )


@router.post("/{session_id}/respond", response_model=StaticRespondResponse)
async def respond_static_chatbot(
    session_id: str,
    data: StaticRespond,
    db: AsyncSession = Depends(get_db)
):
    """Submit a response to the current item in static chatbot."""
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

    if session.session_type != SessionType.STATIC:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not a static chatbot type"
        )

    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed"
        )

    # Current item index (0-based)
    current_idx = session.items_administered
    if current_idx >= 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All items already answered"
        )

    # Get current item
    current_item_num = SURVEY_ORDER[current_idx]
    current_item = MINI_IPIP6_ITEMS[current_item_num]

    # Save response
    response = ItemResponse(
        session_id=session_id,
        item_number=current_item_num,
        trait=current_item["trait"],
        response_value=data.response_value,
        presentation_order=current_idx + 1,
    )
    db.add(response)

    # Update session
    session.items_administered = current_idx + 1

    # Check if complete
    is_complete = session.items_administered >= 24

    if is_complete:
        # Get all responses for scoring
        result = await db.execute(
            select(ItemResponse)
            .where(ItemResponse.session_id == session_id)
            .order_by(ItemResponse.presentation_order)
        )
        all_responses = result.scalars().all()
        response_list = [(r.item_number, r.response_value) for r in all_responses]
        response_list.append((current_item_num, data.response_value))

        # Calculate scores
        scores = calculate_all_scores_from_list(response_list)

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

        # Update session
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.duration_seconds = duration

        await db.commit()

        return StaticRespondResponse(
            session_id=session_id,
            is_complete=True,
            next_item_number=None,
            next_item_text=None,
            progress="24/24",
            message="Thank you for completing the assessment! Your responses have been recorded.",
        )
    else:
        # Get next item
        next_idx = session.items_administered
        next_item_num = SURVEY_ORDER[next_idx]
        next_item = MINI_IPIP6_ITEMS[next_item_num]

        await db.commit()

        return StaticRespondResponse(
            session_id=session_id,
            is_complete=False,
            next_item_number=next_item_num,
            next_item_text=next_item["text"],
            progress=f"{session.items_administered}/24",
            message=None,
        )


@router.get("/{session_id}/state")
async def get_static_state(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get current state of static chatbot session."""
    result = await db.execute(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Get current item if not complete
    current_item = None
    if session.items_administered < 24:
        current_item_num = SURVEY_ORDER[session.items_administered]
        current_item = {
            "number": current_item_num,
            "text": MINI_IPIP6_ITEMS[current_item_num]["text"],
            "trait": MINI_IPIP6_ITEMS[current_item_num]["trait"],
        }

    return {
        "session_id": session_id,
        "status": session.status.value,
        "items_administered": session.items_administered,
        "total_items": 24,
        "progress": f"{session.items_administered}/24",
        "current_item": current_item,
        "is_complete": session.status == SessionStatus.COMPLETED,
    }
