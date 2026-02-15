"""
Intent classification node.
Detects the intent and confidence of a support ticket using LLM.
Includes explicit escalation phrase detection.
"""
import logging
import re

from app.services.llm import invoke_llm_json
from app.services.exceptions import LLMError
from app.utils.prompts import INTENT_CLASSIFICATION_PROMPT
from app.schemas.llm_outputs import IntentClassification, FALLBACK_INTENT

logger = logging.getLogger(__name__)

# Phrases that indicate explicit escalation request
ESCALATION_PHRASES = [
    r'\bescalate\b',
    r'\bhuman\s*(support|agent|help|review)?\b',
    r'\btalk\s*to\s*(a\s*)?(human|agent|person|representative)\b',
    r'\bconnect\s*(me\s*)?(to|with)\s*(a\s*)?(human|agent|person)\b',
    r'\breal\s*person\b',
    r'\blive\s*agent\b',
    r'\bspeak\s*(to|with)\s*(someone|agent|human)\b',
    r'\bneed\s*(a\s*)?human\b',
    r'\bget\s*(me\s*)?(a\s*)?(human|agent)\b',
]


def is_escalation_request(text: str) -> bool:
    """Check if the user is explicitly requesting human escalation."""
    text_lower = text.lower()
    for pattern in ESCALATION_PHRASES:
        if re.search(pattern, text_lower):
            return True
    return False


def detect_intent(state: dict) -> dict:
    """
    Classify the intent of the support ticket.
    
    First checks for explicit escalation phrases.
    If not found, uses LLM for classification.
    
    Returns:
        Dict with intent, confidence, and updated status.
        Falls back to safe defaults on LLM failure.
    """
    ticket_text = state["ticket_text"]
    
    # Check for explicit escalation request FIRST
    if is_escalation_request(ticket_text):
        logger.info(f"Explicit escalation request detected for ticket {state['ticket_id']}")
        return {
            "intent": "escalate_request",
            "confidence": 1.0,
            "status": "processing",
            "explicit_escalation": True
        }
    
    # Standard LLM-based classification
    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        ticket_text=ticket_text
    )

    try:
        result = invoke_llm_json(prompt, IntentClassification)
        return {
            "intent": result.intent,
            "confidence": result.confidence,
            "status": "processing",
            "explicit_escalation": False
        }

    except LLMError as e:
        logger.error(f"Intent classification failed for ticket {state['ticket_id']}: {e}")
        # Use fallback - low confidence triggers human review downstream
        return {
            "intent": FALLBACK_INTENT.intent,
            "confidence": FALLBACK_INTENT.confidence,
            "status": "processing",
            "error_message": f"Intent classification failed: {e.message}",
            "explicit_escalation": False
        }
