"""G4: Natural Chatbot API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict
import json

from ..core.database import get_db
from ..core.mini_ipip6_data import TRAITS
from ..models import (
    Participant, AssessmentSession, SessionType, SessionStatus,
    AssessmentResult
)
from ..models.response import ChatLog
from ..schemas import (
    NaturalStartResponse, NaturalMessage, NaturalMessageResponse,
    NaturalAnalyzeResponse, TraitInference
)
from ..services.llm_service import LLMService, llm_service
from ..services.counterbalancing import get_sequence_number
from ..config import settings

router = APIRouter()

# In-memory conversation storage (in production, use Redis or database)
_conversations: Dict[str, List[Dict[str, str]]] = {}


def get_llm_service() -> LLMService:
    """Dependency for LLM service."""
    return llm_service


@router.post("/{participant_id}/start", response_model=NaturalStartResponse)
async def start_natural_chatbot(
    participant_id: str,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
):
    """Start a new natural chatbot session."""
    # Check if LLM is configured
    if not llm.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not configured. Set OPENAI_API_KEY environment variable."
        )

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

    # Check if natural chatbot already completed
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.participant_id == participant_id)
        .where(AssessmentSession.session_type == SessionType.NATURAL)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Natural chatbot already completed for this participant"
        )

    # Get sequence number
    sequence = get_sequence_number(participant.condition_order, "natural")

    # Create new session
    session = AssessmentSession(
        participant_id=participant_id,
        session_type=SessionType.NATURAL,
        sequence_number=sequence,
        status=SessionStatus.IN_PROGRESS,
        turn_count=0,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Initialize conversation with system prompt
    system_prompt = llm.get_system_prompt()
    conversation = [
        {"role": "system", "content": system_prompt}
    ]

    # Generate initial greeting
    initial_message = await llm.generate_response(conversation)
    conversation.append({"role": "assistant", "content": initial_message})

    # Store conversation
    _conversations[session.id] = conversation

    # Save initial chat log
    chat_log = ChatLog(
        session_id=session.id,
        turn_number=0,
        role="assistant",
        content=initial_message,
    )
    db.add(chat_log)

    # Update session
    session.turn_count = 1
    await db.commit()

    return NaturalStartResponse(
        session_id=session.id,
        message=initial_message,
        conversation_id=session.id,
    )


@router.post("/{session_id}/message", response_model=NaturalMessageResponse)
async def send_message(
    session_id: str,
    data: NaturalMessage,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
):
    """Send a message to the natural chatbot and get a response."""
    if not llm.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not configured"
        )

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

    if session.session_type != SessionType.NATURAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not a natural chatbot type"
        )

    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed"
        )

    # Get conversation
    conversation = _conversations.get(session_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation not found. Please restart the session."
        )

    # Add user message
    conversation.append({"role": "user", "content": data.content})

    # Save user chat log
    user_log = ChatLog(
        session_id=session_id,
        turn_number=session.turn_count,
        role="user",
        content=data.content,
    )
    db.add(user_log)

    # Generate response
    response_text = await llm.generate_response(conversation)
    conversation.append({"role": "assistant", "content": response_text})

    # Save assistant chat log
    assistant_log = ChatLog(
        session_id=session_id,
        turn_number=session.turn_count + 1,
        role="assistant",
        content=response_text,
    )
    db.add(assistant_log)

    # Update session
    session.turn_count += 2  # User + Assistant

    # Check if minimum turns reached
    can_analyze = session.turn_count >= settings.NATURAL_MIN_TURNS * 2

    await db.commit()

    return NaturalMessageResponse(
        session_id=session_id,
        message=response_text,
        turn_count=session.turn_count // 2,  # Approximate exchanges
        can_analyze=can_analyze,
    )


@router.post("/{session_id}/analyze", response_model=NaturalAnalyzeResponse)
async def analyze_conversation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
):
    """Analyze the conversation to infer personality traits."""
    if not llm.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not configured"
        )

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

    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already analyzed"
        )

    # Get conversation
    conversation = _conversations.get(session_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation not found"
        )

    # Check minimum turns
    exchanges = session.turn_count // 2
    if exchanges < settings.NATURAL_MIN_TURNS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum {settings.NATURAL_MIN_TURNS} conversation exchanges required. Current: {exchanges}"
        )

    # Analyze personality
    inference_result = await llm.analyze_personality(conversation)
    validated_result = llm.validate_inference_result(inference_result)

    # Calculate duration
    duration = int((datetime.utcnow() - session.started_at).total_seconds())

    # Create result
    result_obj = AssessmentResult(
        session_id=session_id,
        extraversion_score=validated_result["extraversion"]["score"],
        agreeableness_score=validated_result["agreeableness"]["score"],
        conscientiousness_score=validated_result["conscientiousness"]["score"],
        neuroticism_score=validated_result["neuroticism"]["score"],
        openness_score=validated_result["openness"]["score"],
        honesty_humility_score=validated_result["honesty_humility"]["score"],
        llm_reasoning=validated_result,
        conversation_turns=exchanges,
        total_items_administered=0,  # No items in natural chatbot
        total_duration_seconds=duration,
    )
    db.add(result_obj)

    # Update session
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.utcnow()
    session.duration_seconds = duration

    # Clean up conversation
    del _conversations[session_id]

    await db.commit()

    # Build response
    inferred_traits = {
        trait: TraitInference(
            score=data["score"],
            confidence=data["confidence"],
            evidence=data["evidence"],
        )
        for trait, data in validated_result.items()
    }

    return NaturalAnalyzeResponse(
        session_id=session_id,
        inferred_traits=inferred_traits,
        conversation_turns=exchanges,
        analysis_model=llm.model,
    )


@router.get("/{session_id}/history")
async def get_conversation_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the conversation history for a session."""
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

    # Get chat logs from database
    result = await db.execute(
        select(ChatLog)
        .where(ChatLog.session_id == session_id)
        .order_by(ChatLog.turn_number)
    )
    logs = result.scalars().all()

    return {
        "session_id": session_id,
        "turn_count": session.turn_count,
        "messages": [
            {
                "role": log.role,
                "content": log.content,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ],
    }


@router.get("/{session_id}/state")
async def get_natural_state(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get current state of natural chatbot session."""
    result = await db.execute(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    exchanges = session.turn_count // 2

    return {
        "session_id": session_id,
        "status": session.status.value,
        "turn_count": session.turn_count,
        "exchanges": exchanges,
        "min_exchanges_required": settings.NATURAL_MIN_TURNS,
        "can_analyze": exchanges >= settings.NATURAL_MIN_TURNS,
        "is_complete": session.status == SessionStatus.COMPLETED,
    }
