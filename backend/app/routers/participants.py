"""Participant management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from ..core.database import get_db
from ..models import Participant, AssessmentSession, SessionStatus
from ..schemas import ParticipantCreate, ParticipantResponse, ParticipantProgress
from ..services.counterbalancing import assign_condition_order, get_next_condition

router = APIRouter()


async def get_next_participant_number(db: AsyncSession) -> int:
    """Get the next participant number."""
    result = await db.execute(select(func.count(Participant.id)))
    count = result.scalar()
    return count + 1


def generate_participant_code(number: int) -> str:
    """Generate participant code like P001, P002, etc."""
    return f"P{number:03d}"


@router.post("/register", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def register_participant(
    data: ParticipantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new participant.

    Assigns Latin Square counterbalancing order automatically.
    """
    # Get next participant number
    participant_number = await get_next_participant_number(db)

    # Generate code and assign condition order
    participant_code = generate_participant_code(participant_number)
    assignment = assign_condition_order(participant_number)

    # Create participant
    participant = Participant(
        participant_code=participant_code,
        age=data.age,
        gender=data.gender,
        education_level=data.education_level,
        latin_square_row=assignment["latin_square_row"],
        condition_order=assignment["condition_order"],
    )

    db.add(participant)
    await db.commit()
    await db.refresh(participant)

    return participant


@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(
    participant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get participant by ID."""
    result = await db.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    return participant


@router.get("/code/{participant_code}", response_model=ParticipantResponse)
async def get_participant_by_code(
    participant_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get participant by code."""
    result = await db.execute(
        select(Participant).where(Participant.participant_code == participant_code)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    return participant


@router.get("/{participant_id}/progress", response_model=ParticipantProgress)
async def get_participant_progress(
    participant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get participant's assessment progress."""
    # Get participant
    result = await db.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    # Get completed sessions
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    completed_sessions = result.scalars().all()
    completed_conditions = [s.session_type.value for s in completed_sessions]

    # Determine next condition
    next_condition = get_next_condition(
        participant.condition_order,
        completed_conditions
    )

    return ParticipantProgress(
        participant_id=participant.id,
        participant_code=participant.participant_code,
        condition_order=participant.condition_order,
        completed_conditions=completed_conditions,
        next_condition=next_condition,
        sessions_completed=len(completed_conditions),
        sessions_remaining=2 - len(completed_conditions),
    )


@router.get("/", response_model=List[ParticipantResponse])
async def list_participants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all participants."""
    result = await db.execute(
        select(Participant)
        .offset(skip)
        .limit(limit)
        .order_by(Participant.created_at.desc())
    )
    return result.scalars().all()
