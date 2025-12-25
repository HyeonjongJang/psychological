"""Item response database model."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped

from ..core.database import Base

if TYPE_CHECKING:
    from .session import AssessmentSession


class ItemResponse(Base):
    """
    Item response model.

    Stores individual item responses with IRT tracking data
    for DOSE chatbot sessions.
    """
    __tablename__ = "item_responses"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Foreign key to session
    session_id = Column(
        String(36),
        ForeignKey("assessment_sessions.id"),
        nullable=False,
        index=True
    )

    # Item information
    item_number = Column(Integer, nullable=False)  # 1-24
    trait = Column(String(30), nullable=False)
    response_value = Column(Integer, nullable=False)  # 1-7 Likert scale
    response_time_ms = Column(Integer, nullable=True)

    # DOSE IRT tracking
    theta_before = Column(Float, nullable=True)
    theta_after = Column(Float, nullable=True)
    se_before = Column(Float, nullable=True)
    se_after = Column(Float, nullable=True)
    fisher_information = Column(Float, nullable=True)

    # Presentation order (for all chatbot types)
    presentation_order = Column(Integer, nullable=False)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session: Mapped["AssessmentSession"] = relationship(
        "AssessmentSession",
        back_populates="responses"
    )

    def __repr__(self):
        return f"<ItemResponse item={self.item_number} value={self.response_value}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "item_number": self.item_number,
            "trait": self.trait,
            "response_value": self.response_value,
            "response_time_ms": self.response_time_ms,
            "theta_before": self.theta_before,
            "theta_after": self.theta_after,
            "se_before": self.se_before,
            "se_after": self.se_after,
            "fisher_information": self.fisher_information,
            "presentation_order": self.presentation_order,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class ChatLog(Base):
    """
    Chat conversation log for Natural chatbot (G4).

    Stores turn-by-turn conversation history.
    """
    __tablename__ = "chat_logs"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Foreign key to session
    session_id = Column(
        String(36),
        ForeignKey("assessment_sessions.id"),
        nullable=False,
        index=True
    )

    # Turn information
    turn_number = Column(Integer, nullable=False)
    role = Column(String(20), nullable=False)  # "system", "assistant", "user"
    content = Column(Text, nullable=False)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChatLog turn={self.turn_number} role={self.role}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
