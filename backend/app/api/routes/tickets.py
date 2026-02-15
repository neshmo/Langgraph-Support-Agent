"""
Ticket API routes.
Handles ticket creation and processing.
"""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_db
from app.graph.graph import build_graph
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.schemas.response import TicketResponse, TicketResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Build graph once at module load
_graph = None


def get_graph():
    """Lazy load the graph to avoid import-time issues."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


@router.post("/", response_model=TicketResponse)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create and process a new support ticket.
    
    The ticket is saved immediately, then processed through the LangGraph workflow.
    If processing fails, the ticket is marked as failed but still persisted.
    """
    ticket_id = str(uuid.uuid4())

    # Create ticket record first
    ticket = Ticket(
        id=ticket_id,
        text=payload.text,
        status="processing"
    )
    
    try:
        db.add(ticket)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to create ticket")

    # Process through graph
    try:
        graph = get_graph()
        result = graph.invoke({
            "ticket_id": ticket_id,
            "ticket_text": payload.text,
            "needs_human": False,
            "status": "processing"
        })

        # Update ticket with results
        ticket.intent = result.get("intent")
        ticket.confidence = result.get("confidence")
        ticket.proposed_solution = result.get("proposed_solution")
        ticket.status = result.get("status", "resolved")
        ticket.error_message = result.get("error_message")
        
        db.commit()

        return TicketResponse(
            ticket_id=ticket_id,
            status=ticket.status,
            result=TicketResult(
                status=ticket.status,
                ticket_text=payload.text,
                intent=ticket.intent,
                confidence=ticket.confidence,
                proposed_solution=ticket.proposed_solution,
                final_response=result.get("final_response"),
                error_message=ticket.error_message
            )
        )

    except Exception as e:
        # Mark ticket as failed but don't lose it
        logger.error(f"Ticket processing failed: {e}")
        ticket.status = "failed"
        ticket.error_message = str(e)
        
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()

        return TicketResponse(
            ticket_id=ticket_id,
            status="failed",
            result=TicketResult(
                status="failed",
                error_message=str(e)
            )
        )


from typing import List, Optional

@router.get("/", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List tickets with optional status filter.
    Most useful for agents finding tickets needed human review.
    """
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    
    tickets = query.order_by(Ticket.created_at.desc()).limit(limit).all()
    
    return [
        TicketResponse(
            ticket_id=t.id,
            status=t.status,
            result=TicketResult(
                status=t.status,
                ticket_text=t.text,
                intent=t.intent,
                confidence=t.confidence,
                proposed_solution=t.proposed_solution,
                error_message=t.error_message
            )
        )
        for t in tickets
    ]

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a ticket by ID."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse(
        ticket_id=ticket.id,
        status=ticket.status,
        result=TicketResult(
            status=ticket.status,
            ticket_text=ticket.text,
            intent=ticket.intent,
            confidence=ticket.confidence,
            proposed_solution=ticket.proposed_solution
        )
    )

# Streaming Implementation
import threading
import queue
import json
from fastapi.responses import StreamingResponse

@router.post("/stream", response_class=StreamingResponse)
def stream_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Stream a ticket response using Server-Sent Events (SSE).
    This allows the frontend to display the AI's response token-by-token.
    
    If ticket_id is provided, this is a follow-up on an existing ticket.
    The original ticket text is preserved as context for Review Queue.
    """
    stream_queue = queue.Queue()
    
    # Check if this is a follow-up on existing ticket
    is_followup = payload.ticket_id is not None
    original_ticket_text = None
    
    if is_followup:
        # Use existing ticket
        ticket_id = payload.ticket_id
        existing_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if existing_ticket:
            # If the previous interaction was dismissed (e.g. off-topic),
            # treat this new message as the valid ticket context.
            if existing_ticket.status == "dismissed":
                existing_ticket.text = payload.text
                original_ticket_text = payload.text
            else:
                original_ticket_text = existing_ticket.text  # Preserve original context
            
            existing_ticket.status = "processing"
            db.commit()
        else:
            # Ticket not found, create new one
            is_followup = False
    
    if not is_followup:
        # Create new ticket
        ticket_id = str(uuid.uuid4())
        original_ticket_text = payload.text
        ticket = Ticket(
            id=ticket_id,
            text=payload.text,
            status="processing"
        )
        try:
            db.add(ticket)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create ticket: {e}")
            raise HTTPException(status_code=500, detail="Failed to create ticket")

    # Background definition: What runs in the thread
    def run_graph_in_background():
        try:
            graph = get_graph()
            
            # Invoke graph with queue injected into config
            # Use current message text but keep original context for display
            result = graph.invoke(
                {
                    "ticket_id": ticket_id,
                    "ticket_text": payload.text,  # Current message for processing
                    "original_ticket_text": original_ticket_text,  # Original for review queue
                    "needs_human": False,
                    "status": "processing"
                },
                config={
                    "configurable": {
                        "stream_queue": stream_queue
                    }
                }
            )

            # Update ticket in DB with new session (thread-safe)
            from app.db.session import SessionLocal
            thread_db = SessionLocal()
            try:
                ticket_record = thread_db.query(Ticket).filter(Ticket.id == ticket_id).first()
                if ticket_record:
                    ticket_record.intent = result.get("intent")
                    ticket_record.confidence = result.get("confidence")
                    ticket_record.proposed_solution = result.get("proposed_solution")
                    ticket_record.status = result.get("status", "resolved")
                    ticket_record.error_message = result.get("error_message")
                    thread_db.commit()
                    logger.info(f"Updated ticket {ticket_id} with status: {ticket_record.status}")
            except SQLAlchemyError as db_err:
                thread_db.rollback()
                logger.error(f"Failed to update ticket {ticket_id}: {db_err}")
            finally:
                thread_db.close()
            
            # Signal Completion
            stream_queue.put({"type": "final_result", "data": result})

        except Exception as e:
            logger.error(f"Background processing failed: {e}")
            stream_queue.put({"type": "error", "error": str(e)})
        finally:
            stream_queue.put(None) # Sentinel

    # Start thread
    thread = threading.Thread(target=run_graph_in_background)
    thread.start()

    # Generator: Yields SSE events
    def event_generator():
        # Yield initial ticket ID
        yield f"data: {json.dumps({'type': 'ticket_id', 'id': ticket_id})}\n\n"

        while True:
            item = stream_queue.get()
            
            if item is None: # Done
                break
            
            if isinstance(item, dict) and item.get("type") in ["final_result", "error"]:
                # Structured event
                yield f"data: {json.dumps(item)}\n\n"
            else:
                # Raw token chunk (string)
                # JSON encode it to stay safe
                yield f"data: {json.dumps({'type': 'chunk', 'content': item})}\n\n"
                
    return StreamingResponse(event_generator(), media_type="text/event-stream")

