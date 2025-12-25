"""Assessment session database model."""
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped
import enum

from ..core.database import Base

if TYPE_CHECKING:
    from .participant import Participant
    from .response import ItemResponse
    from .result import AssessmentResult


class SessionType(str, enum.Enum):
    """Types of assessment sessions."""
    SURVEY = "survey"
    DOSE = "dose"


class SessionStatus(str, enum.Enum):
    """Status of assessment session."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AssessmentSession(Base):
    """
    Assessment session model.

    Tracks a single assessment instance for a participant,
    including progress, responses, and results.
    """
    __tablename__ = "assessment_sessions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Foreign key to participant
    participant_id = Column(
        String(36),
        ForeignKey("participants.id"),
        nullable=False,
        index=True
    )

    # Session type and order
    session_type = Column(
        Enum(SessionType),
        nullable=False
    )
    sequence_number = Column(Integer, nullable=False)  # 1-4 within participant

    # Status
    status = Column(
        Enum(SessionStatus),
        default=SessionStatus.IN_PROGRESS
    )

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # DOSE-specific tracking (stored as JSON)
    current_theta = Column(JSON, nullable=True)  # {trait: theta_value}
    current_se = Column(JSON, nullable=True)     # {trait: se_value}
    items_administered = Column(Integer, default=0)

    # Natural chatbot specific
    conversation_state = Column(JSON, nullable=True)  # Chat history
    turn_count = Column(Integer, default=0)

    # Relationships
    participant: Mapped["Participant"] = relationship(
        "Participant",
        back_populates="sessions"
    )
    responses: Mapped[List["ItemResponse"]] = relationship(
        "ItemResponse",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    result: Mapped[Optional["AssessmentResult"]] = relationship(
        "AssessmentResult",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AssessmentSession {self.id[:8]} ({self.session_type.value})>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "session_type": self.session_type.value,
            "sequence_number": self.sequence_number,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "items_administered": self.items_administered,
            "turn_count": self.turn_count,
        }
