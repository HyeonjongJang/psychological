"""G3: DOSE Adaptive Chatbot API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json

from ..core.database import get_db
from ..core.mini_ipip6_data import MINI_IPIP6_ITEMS, TRAITS
from ..models import (
    Participant, AssessmentSession, SessionType, SessionStatus,
    ItemResponse, AssessmentResult
)
from ..schemas import (
    DOSEStartResponse, DOSERespond, DOSERespondResponse,
    TraitEstimate, DOSEProgress
)
from ..services.dose_algorithm import DOSEAlgorithm, DOSESessionState, DOSEAction
from ..services.counterbalancing import get_sequence_number
from ..services.irt_engine import irt_engine

router = APIRouter()

# In-memory session state storage (in production, use Redis or database)
_dose_states: dict[str, DOSESessionState] = {}


def get_dose_algorithm() -> DOSEAlgorithm:
    """Dependency for DOSE algorithm."""
    return DOSEAlgorithm()


@router.post("/{participant_id}/start", response_model=DOSEStartResponse)
async def start_dose_chatbot(
    participant_id: str,
    db: AsyncSession = Depends(get_db),
    dose: DOSEAlgorithm = Depends(get_dose_algorithm)
):
    """Start a new DOSE adaptive chatbot session."""
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

    # Check if DOSE already completed
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.session_type == SessionType.DOSE)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DOSE chatbot already completed for this participant"
        )

    # Get sequence number
    sequence = get_sequence_number(participant.condition_order, "dose")

    # Initialize DOSE session state
    dose_state = dose.initialize_session()

    # Create database session
    session = AssessmentSession(
        participant_id=participant_id,
        session_type=SessionType.DOSE,
        sequence_number=sequence,
        status=SessionStatus.IN_PROGRESS,
        items_administered=0,
        current_theta={trait: 0.0 for trait in TRAITS},
        current_se={trait: 1.0 for trait in TRAITS},
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Store DOSE state
    _dose_states[session.id] = dose_state

    # Get first action (which item to present)
    action = dose.get_next_action(dose_state)

    # Build response
    current_estimates = {
        trait: TraitEstimate(
            theta=data["theta"],
            se=data["se"],
            items_administered=data["items_administered"],
            completed=data["completed"],
        )
        for trait, data in action["current_estimates"].items()
    }

    return DOSEStartResponse(
        session_id=session.id,
        message="Hi! I'm going to ask you some questions to understand your personality. This is an adaptive assessment - I'll select questions based on your responses to get the most accurate picture efficiently.",
        current_item={
            "number": action["item_number"],
            "text": action["item_text"],
            "trait": action["trait"],
        },
        current_estimates=current_estimates,
    )


@router.post("/{session_id}/respond", response_model=DOSERespondResponse)
async def respond_dose_chatbot(
    session_id: str,
    data: DOSERespond,
    db: AsyncSession = Depends(get_db),
    dose: DOSEAlgorithm = Depends(get_dose_algorithm)
):
    """Submit a response to the current item in DOSE chatbot."""
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

    if session.session_type != SessionType.DOSE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not a DOSE chatbot type"
        )

    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed"
        )

    # Get DOSE state
    dose_state = _dose_states.get(session_id)
    if not dose_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DOSE session state not found. Please restart the session."
        )

    # Get current item to respond to
    current_action = dose.get_next_action(dose_state)
    if current_action["action"] == DOSEAction.COMPLETE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment already complete"
        )

    current_item_num = current_action["item_number"]
    current_item = MINI_IPIP6_ITEMS[current_item_num]

    # Get theta/SE before update
    trait = current_item["trait"]
    theta_before = dose_state.trait_states[trait].theta_estimate
    se_before = dose_state.trait_states[trait].standard_error

    # Process response through DOSE algorithm
    dose_state = dose.process_response(dose_state, current_item_num, data.response_value)

    # Get theta/SE after update
    theta_after = dose_state.trait_states[trait].theta_estimate
    se_after = dose_state.trait_states[trait].standard_error

    # Calculate Fisher information
    fisher_info = irt_engine.item_fisher_information(current_item_num, theta_before)

    # Save response to database
    response = ItemResponse(
        session_id=session_id,
        item_number=current_item_num,
        trait=trait,
        response_value=data.response_value,
        presentation_order=dose_state.total_items,
        theta_before=theta_before,
        theta_after=theta_after,
        se_before=se_before,
        se_after=se_after,
        fisher_information=fisher_info,
    )
    db.add(response)

    # Update session
    session.items_administered = dose_state.total_items
    session.current_theta = {
        t: dose_state.trait_states[t].theta_estimate for t in TRAITS
    }
    session.current_se = {
        t: dose_state.trait_states[t].standard_error for t in TRAITS
    }

    # Get next action
    next_action = dose.get_next_action(dose_state)

    # Build estimates
    current_estimates = {
        trait: TraitEstimate(
            theta=est_data["theta"],
            se=est_data["se"],
            items_administered=est_data["items_administered"],
            completed=est_data["completed"],
        )
        for trait, est_data in next_action["current_estimates"].items()
    }

    progress = DOSEProgress(
        items_administered=dose_state.total_items,
        traits_completed=sum(dose_state.traits_completed.values()),
        total_traits=6,
    )

    if next_action["action"] == DOSEAction.COMPLETE:
        # Assessment complete - save results
        final_results = dose.get_final_results(dose_state)

        # Calculate duration
        duration = int((datetime.utcnow() - session.started_at).total_seconds())

        # Create result with Likert-scale scores
        result_obj = AssessmentResult(
            session_id=session_id,
            extraversion_score=final_results["trait_estimates"]["extraversion"]["likert_score"],
            agreeableness_score=final_results["trait_estimates"]["agreeableness"]["likert_score"],
            conscientiousness_score=final_results["trait_estimates"]["conscientiousness"]["likert_score"],
            neuroticism_score=final_results["trait_estimates"]["neuroticism"]["likert_score"],
            openness_score=final_results["trait_estimates"]["openness"]["likert_score"],
            honesty_humility_score=final_results["trait_estimates"]["honesty_humility"]["likert_score"],
            extraversion_se=final_results["trait_estimates"]["extraversion"]["standard_error"],
            agreeableness_se=final_results["trait_estimates"]["agreeableness"]["standard_error"],
            conscientiousness_se=final_results["trait_estimates"]["conscientiousness"]["standard_error"],
            neuroticism_se=final_results["trait_estimates"]["neuroticism"]["standard_error"],
            openness_se=final_results["trait_estimates"]["openness"]["standard_error"],
            honesty_humility_se=final_results["trait_estimates"]["honesty_humility"]["standard_error"],
            total_items_administered=final_results["total_items_administered"],
            total_duration_seconds=duration,
            item_reduction_rate=final_results["item_reduction_rate"],
        )
        db.add(result_obj)

        # Update session
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.duration_seconds = duration

        # Clean up state
        del _dose_states[session_id]

        await db.commit()

        return DOSERespondResponse(
            session_id=session_id,
            action="complete",
            next_item=None,
            current_estimates=current_estimates,
            progress=progress,
            stopping_reason=f"All traits estimated with sufficient precision (SE < {dose.se_threshold})",
        )
    else:
        await db.commit()

        return DOSERespondResponse(
            session_id=session_id,
            action="present_item",
            next_item={
                "number": next_action["item_number"],
                "text": next_action["item_text"],
                "trait": next_action["trait"],
            },
            current_estimates=current_estimates,
            progress=progress,
            stopping_reason=None,
        )


@router.get("/{session_id}/state")
async def get_dose_state(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get current state of DOSE chatbot session."""
    result = await db.execute(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Get DOSE state if available
    dose_state = _dose_states.get(session_id)

    return {
        "session_id": session_id,
        "status": session.status.value,
        "items_administered": session.items_administered,
        "current_theta": session.current_theta,
        "current_se": session.current_se,
        "traits_completed": dose_state.traits_completed if dose_state else None,
        "is_complete": session.status == SessionStatus.COMPLETED,
    }
