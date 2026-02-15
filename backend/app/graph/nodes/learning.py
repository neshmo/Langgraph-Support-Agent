"""
Learning node.
Converts human feedback into knowledge base documents.
"""
import logging

from app.services.knowledge_base import add_knowledge_document

logger = logging.getLogger(__name__)


def learning_from_feedback(state: dict) -> dict:
    """
    Learn from human feedback by adding to knowledge base.
    
    Returns:
        Dict with updated status.
    """
    feedback = state.get("human_feedback")
    solution = state.get("final_response")

    if not feedback or not solution:
        return {}

    document_text = f"""Issue: {state['ticket_text']}

Resolution: {solution}

Agent Notes: {feedback}"""

    try:
        add_knowledge_document(
            text=document_text,
            metadata={
                "source": "human_feedback",
                "ticket_id": state["ticket_id"],
                "intent": state.get("intent")
            }
        )
        logger.info(f"Learned from feedback for ticket {state['ticket_id']}")
        return {"status": "learned"}
    
    except Exception as e:
        logger.error(f"Failed to learn from feedback: {e}")
        return {}
