"""
Confidence thresholds and utilities.
"""

CONFIDENCE_THRESHOLD = 0.85


def needs_human_review(confidence: float | None) -> bool:
    """
    Determine whether human review is required based on confidence.
    
    Args:
        confidence: Classification confidence score (0.0 - 1.0)
    
    Returns:
        True if human review is needed.
    """
    if confidence is None:
        return True
    return confidence < CONFIDENCE_THRESHOLD
