"""
Knowledge retrieval node.
Retrieves relevant documents from the knowledge base for context.
"""
import logging

from app.services.knowledge_base import search_knowledge_base

logger = logging.getLogger(__name__)


def retrieve_knowledge(state: dict) -> dict:
    """
    Retrieve relevant KB docs for the ticket.
    
    Returns:
        Dict with retrieved_docs list.
        Returns empty list on failure (non-critical).
    """
    try:
        results = search_knowledge_base(state["ticket_text"], k=3)
        return {"retrieved_docs": results}
    
    except Exception as e:
        logger.warning(f"Knowledge retrieval failed: {e}")
        # Non-critical - continue without context
        return {"retrieved_docs": []}
