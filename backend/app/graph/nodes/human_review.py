"""
Human review node.
Marks ticket for human escalation and prepares review payload.
"""


def human_review(state: dict) -> dict:
    """
    Prepare ticket for human review.
    
    Returns:
        Dict with status and final_response containing review details.
    """
    return {
        "status": "waiting_human",
        "final_response": {
            "message": "This ticket requires human review",
            "ticket_id": state["ticket_id"],
            "proposed_solution": state.get("proposed_solution"),
            "confidence": state.get("confidence"),
            "intent": state.get("intent")
        }
    }
