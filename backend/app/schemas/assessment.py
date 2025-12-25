"""Pydantic schemas for assessment endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# === Session Schemas ===

class SessionStart(BaseModel):
    """Schema for starting a new session."""
    participant_id: str
    session_type: str  # survey, static, dose, natural


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: str
    participant_id: str
    session_type: str
    sequence_number: int
    status: str
    started_at: datetime
    items_administered: int = 0

    class Config:
        from_attributes = True


# === Survey (G1) Schemas ===

class SurveyItem(BaseModel):
    """Schema for a survey item."""
    item_number: int
    text: str
    trait: str


class SurveyItemsResponse(BaseModel):
    """Schema for returning all survey items."""
    session_id: str
    items: List[SurveyItem]
    total_items: int = 24


class SurveyResponseItem(BaseModel):
    """Schema for a single item response."""
    item_number: int = Field(..., ge=1, le=24)
    value: int = Field(..., ge=1, le=7)


class SurveySubmit(BaseModel):
    """Schema for submitting all survey responses."""
    responses: List[SurveyResponseItem] = Field(..., min_length=24, max_length=24)


# === Static Chatbot (G2) Schemas ===

class StaticStartResponse(BaseModel):
    """Schema for starting static chatbot."""
    session_id: str
    message: str
    current_item: int
    item_text: str
    total_items: int = 24


class StaticRespond(BaseModel):
    """Schema for static chatbot response."""
    response_value: int = Field(..., ge=1, le=7)


class StaticRespondResponse(BaseModel):
    """Schema for static chatbot response result."""
    session_id: str
    is_complete: bool
    next_item_number: Optional[int] = None
    next_item_text: Optional[str] = None
    progress: str  # "3/24"
    message: Optional[str] = None


# === DOSE Chatbot (G3) Schemas ===

class TraitEstimate(BaseModel):
    """Schema for a single trait estimate."""
    theta: float
    se: float
    items_administered: int
    completed: bool = False


class DOSEStartResponse(BaseModel):
    """Schema for starting DOSE chatbot."""
    session_id: str
    message: str
    current_item: Dict[str, Any]  # {number, text, trait}
    current_estimates: Dict[str, TraitEstimate]


class DOSERespond(BaseModel):
    """Schema for DOSE chatbot response."""
    response_value: int = Field(..., ge=1, le=7)


class DOSEProgress(BaseModel):
    """Schema for DOSE progress."""
    items_administered: int
    traits_completed: int
    total_traits: int = 6


class DOSERespondResponse(BaseModel):
    """Schema for DOSE response result."""
    session_id: str
    action: str  # "present_item" or "complete"
    next_item: Optional[Dict[str, Any]] = None
    current_estimates: Dict[str, TraitEstimate]
    progress: DOSEProgress
    stopping_reason: Optional[str] = None


# === Natural Chatbot (G4) Schemas ===

class NaturalStartResponse(BaseModel):
    """Schema for starting natural chatbot."""
    session_id: str
    message: str
    conversation_id: str


class NaturalMessage(BaseModel):
    """Schema for sending a message to natural chatbot."""
    content: str = Field(..., min_length=1, max_length=2000)


class NaturalMessageResponse(BaseModel):
    """Schema for natural chatbot response."""
    session_id: str
    message: str
    turn_count: int
    can_analyze: bool  # True if min turns reached


class TraitInference(BaseModel):
    """Schema for inferred trait."""
    score: float
    confidence: str  # "high", "medium", "low"
    evidence: str


class NaturalAnalyzeResponse(BaseModel):
    """Schema for natural chatbot analysis result."""
    session_id: str
    inferred_traits: Dict[str, TraitInference]
    conversation_turns: int
    analysis_model: str = "gpt-4"


# === Results Schemas ===

class TraitScore(BaseModel):
    """Schema for a trait score."""
    score: float
    standard_error: Optional[float] = None


class SessionResult(BaseModel):
    """Schema for session results."""
    session_id: str
    session_type: str
    scores: Dict[str, TraitScore]
    metrics: Dict[str, Any]
    completed_at: Optional[datetime] = None


class ComparisonResult(BaseModel):
    """Schema for comparison between sessions."""
    correlation: float
    mae: float
    rmse: float
    differences: Dict[str, float]


class ParticipantResults(BaseModel):
    """Schema for participant's complete results."""
    participant_id: str
    participant_code: str
    sessions: List[SessionResult]
    comparison: Optional[ComparisonResult] = None
