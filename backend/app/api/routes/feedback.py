"""
Feedback API routes.
Handles human feedback submission for learning.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.feedback import FeedbackCreate
from app.schemas.response import FeedbackResponse
from app.graph.nodes.learning import learning_from_feedback
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submit human feedback for a ticket.
    
    This feedback is used to improve the knowledge base.
    """
    # Verify ticket exists
    ticket = db.query(Ticket).filter(Ticket.id == payload.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    state = {
        "ticket_id": payload.ticket_id,
        "ticket_text": payload.ticket_text,
        "final_response": payload.final_response,
        "human_feedback": payload.feedback,
        "intent": ticket.intent
    }

    try:
        learning_from_feedback(state)
        
        # FIX: Update ticket status to resolved so it doesn't reappear in queue
        ticket.status = "resolved"
        db.commit()
        
        return FeedbackResponse(
            status="feedback_processed",
            ticket_id=payload.ticket_id,
            message="Feedback recorded and added to knowledge base"
        )
    
    except Exception as e:
        logger.error(f"Failed to process feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process feedback"
        )
