"""
Pydantic schemas for LLM response validation.
These enforce structured JSON outputs from the LLM.
"""
from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    """Schema for intent classification LLM output."""
    intent: str = Field(description="The classified intent of the support ticket")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )


class SolutionOutput(BaseModel):
    """Schema for solution generation LLM output."""
    solution: str = Field(description="Step-by-step solution for the customer")
    requires_followup: bool = Field(
        default=False,
        description="Whether this issue needs follow-up"
    )


# Default fallbacks for when LLM fails
FALLBACK_INTENT = IntentClassification(intent="unknown", confidence=0.0)
FALLBACK_SOLUTION = SolutionOutput(
    solution="We apologize, but we're unable to generate a solution at this time. A support agent will review your request shortly.",
    requires_followup=True
)
