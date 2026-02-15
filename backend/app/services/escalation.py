"""
Escalation service.
Prepares structured payloads for human review.
"""
from app.schemas.response import EscalationPayload


def build_escalation_payload(state: dict) -> dict:
    """
    Prepare structured data for human support agent.
    
    Returns:
        Dict matching EscalationPayload schema.
    """
    return EscalationPayload(
        ticket_id=state["ticket_id"],
        ticket_text=state["ticket_text"],
        intent=state.get("intent"),
        confidence=state.get("confidence"),
        proposed_solution=state.get("proposed_solution"),
        reason=_determine_escalation_reason(state)
    ).model_dump()


def _determine_escalation_reason(state: dict) -> str:
    """Determine why this ticket was escalated."""
    confidence = state.get("confidence", 0.0)
    
    if state.get("error_message"):
        return f"Processing error: {state['error_message']}"
    
    if confidence < 0.5:
        return "Very low confidence in classification"
    
    if confidence < 0.85:
        return "Confidence below threshold for automated resolution"
    
    return "Flagged for human review"
