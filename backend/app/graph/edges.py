"""
Edge routing functions for LangGraph workflow.
Determines conditional transitions between nodes.
"""


def route_after_intent(state: dict) -> str:
    """
    Decide routing after intent classification.
    
    Routes to:
    - escalate: If user explicitly requested human support
    - continue: Otherwise, proceed to solution generation
    """
    if state.get("explicit_escalation") or state.get("intent") == "escalate_request":
        return "escalate"
    if state.get("intent") == "off_topic":
        return "off_topic"
    return "continue"


def route_after_solution(state: dict) -> str:
    """
    Decide the next step after solution generation.
    
    Routes to:
    - escalate: If human review is needed (low confidence)
    - finish: If ticket is resolved
    """
    if state.get("needs_human"):
        return "escalate"
    return "finish"


def route_on_failure(state: dict) -> str:
    """
    Check if the workflow should fail early.
    
    Routes to:
    - failed: If there's a critical error
    - continue: Otherwise
    """
    if state.get("status") == "failed":
        return "failed"
    return "continue"
