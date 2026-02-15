"""
LangGraph state definition for the support agent workflow.
"""
from typing import TypedDict, Optional, List, Any


class SupportState(TypedDict):
    """
    State object passed through the LangGraph workflow.
    
    Status values:
    - processing: Ticket is being processed
    - resolved: Successfully resolved by AI
    - waiting_human: Escalated for human review
    - failed: Processing failed (LLM error, etc.)
    """
    # Required fields
    ticket_id: str
    ticket_text: str
    
    # Status tracking
    status: str  # processing, resolved, waiting_human, failed
    
    # Intent classification
    intent: Optional[str]
    confidence: Optional[float]
    explicit_escalation: Optional[bool]  # True when user explicitly requests human
    
    # Solution generation
    proposed_solution: Optional[str]
    needs_human: bool
    
    # Final output
    final_response: Optional[Any]
    
    # Error tracking
    error_message: Optional[str]
    
    # Retrieved context (for RAG)
    retrieved_docs: Optional[List[dict]]
