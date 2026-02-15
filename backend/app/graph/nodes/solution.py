"""
Solution generation node.
Generates a solution for the support ticket using LLM.
Supports prose streaming for real-time token display.
"""
import logging

from app.services.llm import invoke_llm, invoke_llm_stream, invoke_llm_json
from app.services.exceptions import LLMError
from app.utils.prompts import SOLUTION_GENERATION_PROMPT, SOLUTION_GENERATION_PROMPT_PROSE
from app.utils.confidence import needs_human_review
from app.schemas.llm_outputs import SolutionOutput, FALLBACK_SOLUTION

logger = logging.getLogger(__name__)


def generate_solution(state: dict, config: dict = None) -> dict:
    """
    Generate a solution for the support ticket.
    
    Uses prose streaming when queue is present for token-by-token display.
    Falls back to JSON mode for non-streaming calls.
    
    Returns:
        Dict with proposed_solution, needs_human flag, and status.
        Falls back to escalation on LLM failure.
    """
    # Extract stream queue from config if present
    stream_queue = None
    if config and "configurable" in config:
        stream_queue = config["configurable"].get("stream_queue")

    # Format retrieved docs for the prompt
    docs = state.get("retrieved_docs") or []
    docs_text = "\n".join(
        [f"- {doc.get('content', '')}" for doc in docs]
    ) if docs else "No relevant knowledge found."

    try:
        if stream_queue:
            # Streaming mode: Use prose prompt for readable token-by-token display
            prompt = SOLUTION_GENERATION_PROMPT_PROSE.format(
                ticket_text=state["ticket_text"],
                intent=state.get("intent", "unknown"),
                retrieved_docs=docs_text
            )
            solution = invoke_llm_stream(prompt, stream_queue)
        else:
            # Non-streaming mode: Use JSON prompt for structured output
            prompt = SOLUTION_GENERATION_PROMPT.format(
                ticket_text=state["ticket_text"],
                intent=state.get("intent", "unknown"),
                retrieved_docs=docs_text
            )
            result = invoke_llm_json(prompt, SolutionOutput)
            solution = result.solution
        
        # Determine if human review is needed based on confidence ONLY
        # High confidence (>=0.85) should NEVER be escalated
        confidence = state.get("confidence")
        needs_human = needs_human_review(confidence)
        
        return {
            "proposed_solution": solution,
            "needs_human": needs_human,
            "status": "waiting_human" if needs_human else "resolved"
        }

    except LLMError as e:
        logger.error(f"Solution generation failed for ticket {state['ticket_id']}: {e}")
        # On failure, escalate to human
        return {
            "proposed_solution": FALLBACK_SOLUTION.solution,
            "needs_human": True,
            "status": "waiting_human",
            "error_message": f"Solution generation failed: {e.message}"
        }
