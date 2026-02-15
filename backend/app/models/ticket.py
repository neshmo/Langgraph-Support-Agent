"""
Ticket database model.
Stores ticket state for persistence and audit.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime

from app.db.base import Base


class Ticket(Base):
    """
    Support ticket database model.
    
    Stores the full state of a ticket for:
    - Audit trail
    - Resumable workflows
    - Analytics
    """
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    
    # Classification
    intent = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Solution
    proposed_solution = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String, default="processing", nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
