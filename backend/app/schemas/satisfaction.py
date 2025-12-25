"""Pydantic schemas for satisfaction survey endpoints."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SatisfactionSubmit(BaseModel):
    """Schema for submitting a satisfaction survey."""
    overall_rating: int = Field(..., ge=1, le=5, description="Overall experience rating (1-5 stars)")
    preferred_method: str = Field(..., pattern="^(survey|dose)$", description="Preferred assessment method")
    dose_ease_of_use: int = Field(..., ge=1, le=7, description="DOSE chatbot ease of use (1-7 Likert)")
    would_recommend: int = Field(..., ge=1, le=7, description="Would recommend to others (1-7 Likert)")
    open_feedback: Optional[str] = Field(None, max_length=2000, description="Open feedback text")
    language: Optional[str] = Field("en", pattern="^(en|kr)$", description="Language used")


class SatisfactionResponse(BaseModel):
    """Schema for satisfaction survey response."""
    id: str
    participant_id: str
    overall_rating: int
    preferred_method: str
    dose_ease_of_use: int
    would_recommend: int
    open_feedback: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SatisfactionStatus(BaseModel):
    """Schema for checking satisfaction survey status."""
    participant_id: str
    has_completed: bool
    survey: Optional[SatisfactionResponse] = None
