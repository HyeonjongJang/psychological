"""Satisfaction survey API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_db
from ..models import Participant, SatisfactionSurvey
from ..schemas import SatisfactionSubmit, SatisfactionResponse, SatisfactionStatus

router = APIRouter()


@router.post("/{participant_id}/submit", response_model=SatisfactionResponse, status_code=status.HTTP_201_CREATED)
async def submit_satisfaction_survey(
    participant_id: str,
    data: SatisfactionSubmit,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a satisfaction survey for a participant.

    Each participant can only submit one satisfaction survey.
    """
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

    # Check if already submitted
    result = await db.execute(
        select(SatisfactionSurvey).where(SatisfactionSurvey.participant_id == participant_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Satisfaction survey already submitted for this participant"
        )

    # Create satisfaction survey
    survey = SatisfactionSurvey(
        participant_id=participant_id,
        overall_rating=data.overall_rating,
        preferred_method=data.preferred_method,
        dose_ease_of_use=data.dose_ease_of_use,
        would_recommend=data.would_recommend,
        open_feedback=data.open_feedback,
        language=data.language,
    )

    db.add(survey)
    await db.commit()
    await db.refresh(survey)

    return survey


@router.get("/{participant_id}/status", response_model=SatisfactionStatus)
async def get_satisfaction_status(
    participant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a participant has completed the satisfaction survey.
    """
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

    # Check for existing survey
    result = await db.execute(
        select(SatisfactionSurvey).where(SatisfactionSurvey.participant_id == participant_id)
    )
    survey = result.scalar_one_or_none()

    return SatisfactionStatus(
        participant_id=participant_id,
        has_completed=survey is not None,
        survey=survey
    )


@router.get("/{participant_id}", response_model=SatisfactionResponse)
async def get_satisfaction_survey(
    participant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the satisfaction survey for a participant.
    """
    result = await db.execute(
        select(SatisfactionSurvey).where(SatisfactionSurvey.participant_id == participant_id)
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Satisfaction survey not found for this participant"
        )

    return survey
