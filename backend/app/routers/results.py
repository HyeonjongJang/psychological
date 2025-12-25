"""Results API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from ..core.database import get_db
from ..core.mini_ipip6_data import TRAITS
from ..models import (
    Participant, AssessmentSession, SessionType, SessionStatus,
    AssessmentResult
)
from ..services.scoring_service import compare_scores

router = APIRouter()


@router.get("/session/{session_id}")
async def get_session_results(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get results for a specific session."""
    # Get session
    result = await db.execute(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session not completed yet"
        )

    # Get result
    result = await db.execute(
        select(AssessmentResult).where(AssessmentResult.session_id == session_id)
    )
    assessment_result = result.scalar_one_or_none()

    if not assessment_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found"
        )

    return {
        "session_id": session_id,
        "session_type": session.session_type.value,
        "sequence_number": session.sequence_number,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "scores": {
            "extraversion": assessment_result.extraversion_score,
            "agreeableness": assessment_result.agreeableness_score,
            "conscientiousness": assessment_result.conscientiousness_score,
            "neuroticism": assessment_result.neuroticism_score,
            "openness": assessment_result.openness_score,
            "honesty_humility": assessment_result.honesty_humility_score,
        },
        "standard_errors": {
            "extraversion": assessment_result.extraversion_se,
            "agreeableness": assessment_result.agreeableness_se,
            "conscientiousness": assessment_result.conscientiousness_se,
            "neuroticism": assessment_result.neuroticism_se,
            "openness": assessment_result.openness_se,
            "honesty_humility": assessment_result.honesty_humility_se,
        } if session.session_type == SessionType.DOSE else None,
        "metrics": {
            "total_items": assessment_result.total_items_administered,
            "duration_seconds": assessment_result.total_duration_seconds,
            "item_reduction_rate": assessment_result.item_reduction_rate,
            "conversation_turns": assessment_result.conversation_turns,
        },
    }


@router.get("/participant/{participant_id}")
async def get_participant_results(
    participant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all results for a participant with comparison."""
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

    # Get completed sessions with results
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
        .order_by(AssessmentSession.sequence_number)
    )
    sessions = result.scalars().all()

    # Build session results
    session_results = []
    scores_by_type = {}

    for session in sessions:
        # Get result
        result = await db.execute(
            select(AssessmentResult).where(AssessmentResult.session_id == session.id)
        )
        assessment_result = result.scalar_one_or_none()

        if assessment_result:
            scores = {
                "extraversion": assessment_result.extraversion_score,
                "agreeableness": assessment_result.agreeableness_score,
                "conscientiousness": assessment_result.conscientiousness_score,
                "neuroticism": assessment_result.neuroticism_score,
                "openness": assessment_result.openness_score,
                "honesty_humility": assessment_result.honesty_humility_score,
            }

            scores_by_type[session.session_type.value] = scores

            session_results.append({
                "session_id": session.id,
                "session_type": session.session_type.value,
                "sequence_number": session.sequence_number,
                "scores": scores,
                "metrics": {
                    "total_items": assessment_result.total_items_administered,
                    "duration_seconds": assessment_result.total_duration_seconds,
                    "item_reduction_rate": assessment_result.item_reduction_rate,
                },
            })

    # Calculate comparisons with survey baseline
    comparisons = {}
    if "survey" in scores_by_type:
        survey_scores = scores_by_type["survey"]
        for session_type, scores in scores_by_type.items():
            if session_type != "survey":
                comparisons[session_type] = compare_scores(survey_scores, scores)

    return {
        "participant_id": participant_id,
        "participant_code": participant.participant_code,
        "condition_order": participant.condition_order,
        "sessions_completed": len(sessions),
        "sessions": session_results,
        "comparisons_with_survey": comparisons if comparisons else None,
    }


@router.get("/comparison/{participant_id}/{type1}/{type2}")
async def compare_session_types(
    participant_id: str,
    type1: str,
    type2: str,
    db: AsyncSession = Depends(get_db)
):
    """Compare results between two session types for a participant."""
    valid_types = {"survey", "dose"}
    if type1 not in valid_types or type2 not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid session type. Must be one of: {valid_types}"
        )

    # Get sessions
    type1_enum = SessionType(type1)
    type2_enum = SessionType(type2)

    result1 = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.session_type == type1_enum)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    session1 = result1.scalar_one_or_none()

    result2 = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.session_type == type2_enum)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    session2 = result2.scalar_one_or_none()

    if not session1 or not session2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both session types not completed"
        )

    # Get results
    r1 = await db.execute(
        select(AssessmentResult).where(AssessmentResult.session_id == session1.id)
    )
    result1_obj = r1.scalar_one_or_none()

    r2 = await db.execute(
        select(AssessmentResult).where(AssessmentResult.session_id == session2.id)
    )
    result2_obj = r2.scalar_one_or_none()

    if not result1_obj or not result2_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found"
        )

    # Build score dicts
    scores1 = {
        "extraversion": result1_obj.extraversion_score,
        "agreeableness": result1_obj.agreeableness_score,
        "conscientiousness": result1_obj.conscientiousness_score,
        "neuroticism": result1_obj.neuroticism_score,
        "openness": result1_obj.openness_score,
        "honesty_humility": result1_obj.honesty_humility_score,
    }

    scores2 = {
        "extraversion": result2_obj.extraversion_score,
        "agreeableness": result2_obj.agreeableness_score,
        "conscientiousness": result2_obj.conscientiousness_score,
        "neuroticism": result2_obj.neuroticism_score,
        "openness": result2_obj.openness_score,
        "honesty_humility": result2_obj.honesty_humility_score,
    }

    comparison = compare_scores(scores1, scores2)

    return {
        "participant_id": participant_id,
        "type1": type1,
        "type2": type2,
        "scores": {
            type1: scores1,
            type2: scores2,
        },
        "comparison": comparison,
    }


@router.get("/aggregate")
async def get_aggregate_results(
    db: AsyncSession = Depends(get_db)
):
    """Get aggregate results across all participants (admin/research endpoint)."""
    # Count participants
    result = await db.execute(select(Participant))
    participants = result.scalars().all()

    # Count completed sessions by type
    session_counts = {}
    for session_type in SessionType:
        result = await db.execute(
            select(AssessmentSession)
            .where(AssessmentSession.session_type == session_type)
            .where(AssessmentSession.status == SessionStatus.COMPLETED)
        )
        sessions = result.scalars().all()
        session_counts[session_type.value] = len(sessions)

    # Calculate average metrics for DOSE sessions
    result = await db.execute(
        select(AssessmentResult)
        .join(AssessmentSession)
        .where(AssessmentSession.session_type == SessionType.DOSE)
    )
    dose_results = result.scalars().all()

    dose_metrics = None
    if dose_results:
        avg_items = sum(r.total_items_administered for r in dose_results) / len(dose_results)
        avg_reduction = sum(r.item_reduction_rate or 0 for r in dose_results) / len(dose_results)
        avg_duration = sum(r.total_duration_seconds for r in dose_results) / len(dose_results)

        dose_metrics = {
            "average_items_administered": avg_items,
            "average_item_reduction_rate": avg_reduction,
            "average_duration_seconds": avg_duration,
            "total_sessions": len(dose_results),
        }

    return {
        "total_participants": len(participants),
        "sessions_completed": session_counts,
        "dose_efficiency_metrics": dose_metrics,
    }
