"""Satisfaction survey database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..core.database import Base


class SatisfactionSurvey(Base):
    """
    Satisfaction survey model for storing user feedback after completing assessments.

    Captures user preferences and experience ratings for research analysis.
    """
    __tablename__ = "satisfaction_surveys"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Foreign key to participant
    participant_id = Column(
        String(36),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Overall experience rating (1-5 stars)
    overall_rating = Column(Integer, nullable=False)

    # Preferred method: "survey" or "dose"
    preferred_method = Column(String(20), nullable=False)

    # DOSE chatbot ease of use (1-7 Likert scale)
    dose_ease_of_use = Column(Integer, nullable=False)

    # Would recommend to others (1-7 Likert scale)
    would_recommend = Column(Integer, nullable=False)

    # Open feedback text (optional)
    open_feedback = Column(Text, nullable=True)

    # Language used during survey
    language = Column(String(10), nullable=True, default="en")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    participant = relationship("Participant", backref="satisfaction_survey")

    def __repr__(self):
        return f"<SatisfactionSurvey {self.id} for participant {self.participant_id}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "overall_rating": self.overall_rating,
            "preferred_method": self.preferred_method,
            "dose_ease_of_use": self.dose_ease_of_use,
            "would_recommend": self.would_recommend,
            "open_feedback": self.open_feedback,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
