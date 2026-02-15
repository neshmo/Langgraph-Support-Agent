"""
API response schemas.
All API responses use these structured models.
"""
from pydantic import BaseModel
from typing import Optional, Any


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str


class EscalationPayload(BaseModel):
    """Payload for escalated tickets requiring human review."""
    ticket_id: str
    ticket_text: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    proposed_solution: Optional[str] = None
    reason: str


class TicketResult(BaseModel):
    """Detailed result from ticket processing."""
    status: str  # resolved, waiting_human, failed
    ticket_text: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    proposed_solution: Optional[str] = None
    final_response: Optional[Any] = None
    error_message: Optional[str] = None
    needs_human: Optional[bool] = None



class TicketResponse(BaseModel):
    """API response for ticket processing."""
    ticket_id: str
    status: str
    result: TicketResult


class FeedbackResponse(BaseModel):
    """API response for feedback submission."""
    status: str
    ticket_id: str
    message: str
