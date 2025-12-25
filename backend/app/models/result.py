"""Assessment result database model."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from ..core.database import Base

if TYPE_CHECKING:
    from .session import AssessmentSession


class AssessmentResult(Base):
    """
    Assessment result model.

    Stores final trait scores and metrics for a completed session.
    """
    __tablename__ = "assessment_results"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Foreign key to session (one-to-one)
    session_id = Column(
        String(36),
        ForeignKey("assessment_sessions.id"),
        unique=True,
        nullable=False
    )

    # Trait scores (1-7 scale for classical, can also store theta)
    extraversion_score = Column(Float, nullable=False)
    agreeableness_score = Column(Float, nullable=False)
    conscientiousness_score = Column(Float, nullable=False)
    neuroticism_score = Column(Float, nullable=False)
    openness_score = Column(Float, nullable=False)
    honesty_humility_score = Column(Float, nullable=False)

    # IRT-specific: Standard Errors (for DOSE)
    extraversion_se = Column(Float, nullable=True)
    agreeableness_se = Column(Float, nullable=True)
    conscientiousness_se = Column(Float, nullable=True)
    neuroticism_se = Column(Float, nullable=True)
    openness_se = Column(Float, nullable=True)
    honesty_humility_se = Column(Float, nullable=True)

    # Natural chatbot specific
    llm_reasoning = Column(JSON, nullable=True)  # Evidence per trait
    conversation_turns = Column(Integer, nullable=True)

    # Metrics
    total_items_administered = Column(Integer, nullable=False)
    total_duration_seconds = Column(Integer, nullable=False)
    item_reduction_rate = Column(Float, nullable=True)  # For DOSE

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session: Mapped["AssessmentSession"] = relationship(
        "AssessmentSession",
        back_populates="result"
    )

    def __repr__(self):
        return f"<AssessmentResult session={self.session_id[:8]}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "scores": {
                "extraversion": self.extraversion_score,
                "agreeableness": self.agreeableness_score,
                "conscientiousness": self.conscientiousness_score,
                "neuroticism": self.neuroticism_score,
                "openness": self.openness_score,
                "honesty_humility": self.honesty_humility_score,
            },
            "standard_errors": {
                "extraversion": self.extraversion_se,
                "agreeableness": self.agreeableness_se,
                "conscientiousness": self.conscientiousness_se,
                "neuroticism": self.neuroticism_se,
                "openness": self.openness_se,
                "honesty_humility": self.honesty_humility_se,
            },
            "llm_reasoning": self.llm_reasoning,
            "metrics": {
                "total_items": self.total_items_administered,
                "duration_seconds": self.total_duration_seconds,
                "item_reduction_rate": self.item_reduction_rate,
                "conversation_turns": self.conversation_turns,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_scores_dict(self):
        """Get just the trait scores as a dict."""
        return {
            "extraversion": self.extraversion_score,
            "agreeableness": self.agreeableness_score,
            "conscientiousness": self.conscientiousness_score,
            "neuroticism": self.neuroticism_score,
            "openness": self.openness_score,
            "honesty_humility": self.honesty_humility_score,
        }
