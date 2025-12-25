"""Participant database model."""
import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from ..core.database import Base

if TYPE_CHECKING:
    from .session import AssessmentSession


class Participant(Base):
    """
    Participant model for storing user information.

    Stores demographic data and Latin Square assignment for
    within-subject counterbalancing.
    """
    __tablename__ = "participants"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Anonymous participant code (e.g., "P001", "P002")
    participant_code = Column(String(50), unique=True, nullable=False, index=True)

    # Optional demographics
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    education_level = Column(String(50), nullable=True)

    # Latin Square counterbalancing
    latin_square_row = Column(Integer, nullable=False)
    condition_order = Column(JSON, nullable=False)  # ["survey", "static", "dose", "natural"]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions: Mapped[List["AssessmentSession"]] = relationship(
        "AssessmentSession",
        back_populates="participant",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Participant {self.participant_code}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "participant_code": self.participant_code,
            "age": self.age,
            "gender": self.gender,
            "education_level": self.education_level,
            "latin_square_row": self.latin_square_row,
            "condition_order": self.condition_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
