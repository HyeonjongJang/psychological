"""Pydantic schemas for participant endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ParticipantCreate(BaseModel):
    """Schema for creating a new participant."""
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = Field(None, max_length=20)
    education_level: Optional[str] = Field(None, max_length=50)


class ParticipantResponse(BaseModel):
    """Schema for participant response."""
    id: str
    participant_code: str
    age: Optional[int] = None
    gender: Optional[str] = None
    education_level: Optional[str] = None
    latin_square_row: int
    condition_order: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ParticipantProgress(BaseModel):
    """Schema for participant progress."""
    participant_id: str
    participant_code: str
    condition_order: List[str]
    completed_conditions: List[str]
    next_condition: Optional[str]
    sessions_completed: int
    sessions_remaining: int
