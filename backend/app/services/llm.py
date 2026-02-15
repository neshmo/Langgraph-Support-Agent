"""
LLM service with retry logic, error handling, and JSON parsing.
Uses OpenRouter API via the OpenAI client.
"""
import json
import time
import logging
from typing import TypeVar, Type

from openai import OpenAI, APIError, RateLimitError, AuthenticationError
from pydantic import BaseModel, ValidationError

from app.config.settings import settings
from app.services.exceptions import (
    LLMError,
    LLMRateLimitError,
    LLMAuthError,
    LLMUnavailableError,
    LLMResponseParseError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0
BACKOFF_MULTIPLIER = 2.0


def _call_llm(prompt: str) -> str:
    """
    Internal LLM call with retry and error mapping.
    Raises custom exceptions on failure.
    """
    last_exception: Exception | None = None
    delay = BASE_DELAY

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=settings.openrouter_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""

        except RateLimitError as e:
            last_exception = LLMRateLimitError(
                f"Rate limit exceeded: {e}", original_error=e
            )
            logger.warning(f"Rate limit hit, retry {attempt + 1}/{MAX_RETRIES}")

        except AuthenticationError as e:
            # Don't retry auth errors
            raise LLMAuthError(f"Authentication failed: {e}", original_error=e)

        except APIError as e:
            if e.status_code in (404, 503):
                last_exception = LLMUnavailableError(
                    f"Service unavailable: {e}", original_error=e
                )
            else:
                last_exception = LLMError(f"API error: {e}", original_error=e)
            logger.warning(f"API error, retry {attempt + 1}/{MAX_RETRIES}: {e}")

        except Exception as e:
            last_exception = LLMError(f"Unexpected error: {e}", original_error=e)
            logger.error(f"Unexpected LLM error: {e}")

        # Exponential backoff
        if attempt < MAX_RETRIES - 1:
            time.sleep(delay)
            delay *= BACKOFF_MULTIPLIER

    raise last_exception or LLMError("LLM call failed after retries")


def invoke_llm(prompt: str) -> str:
    """
    Call the LLM and return raw text response.
    Raises LLMError on failure.
    """
    return _call_llm(prompt)


def invoke_llm_stream(prompt: str, stream_queue) -> str:
    """
    Call the LLM with streaming, pushing tokens to queue for real-time display.
    Returns the complete response text after streaming finishes.
    
    This is used for prose generation where we want token-by-token streaming.
    
    Args:
        prompt: The prompt to send
        stream_queue: Queue to push token chunks to for real-time frontend display
    
    Returns:
        Complete response text
    """
    raw_response = ""
    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            stream=True
        )
        
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                # Push to queue for real-time frontend display
                stream_queue.put(content)
                # Accumulate for backend
                raw_response += content

    except Exception as e:
        logger.error(f"Streaming LLM error: {e}")
        raise LLMError(f"Streaming failed: {e}", original_error=e)
    
    return raw_response


def invoke_llm_json(prompt: str, schema: Type[T], stream_queue=None) -> T:
    """
    Call the LLM and parse response as JSON into a Pydantic model.
    Supports side-channel streaming if stream_queue is provided.
    
    Args:
        prompt: The prompt to send (should instruct JSON output)
        schema: Pydantic model class to validate against
        stream_queue: Optional queue to push token chunks to
    
    Returns:
        Validated Pydantic model instance
    """
    if stream_queue:
        # Streaming Mode
        raw_response = ""
        try:
            # We use the internal client directly for streaming to avoid refactoring _call_llm entirely
            # but we should technically respect the retry logic. 
            # For simplicity in this step, we'll wrap a basic retry or assume _call_llm refactor is too risky for now.
            # Let's simple call the client with stream=True.
            
            response = client.chat.completions.create(
                model=settings.openrouter_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                stream=True
            )
            
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    # Push to queue for frontend
                    stream_queue.put(content)
                    # Accumulate for backend
                    raw_response += content

        except Exception as e:
            logger.error(f"Streaming LLM error: {e}")
            raise LLMError(f"Streaming failed: {e}", original_error=e)
            
    else:
        # Standard Mode
        raw_response = _call_llm(prompt)

    # Clean response - strip markdown code blocks if present
    content = raw_response.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"): # Handle generic block
        content = content[3:]
    
    if content.endswith("```"):
        content = content[:-3]
    
    content = content.strip()

    try:
        data = json.loads(content)
        return schema.model_validate(data)
    except json.JSONDecodeError as e:
        raise LLMResponseParseError(
            f"Invalid JSON in LLM response: {e}",
            original_error=e
        )
    except ValidationError as e:
        raise LLMResponseParseError(
            f"LLM response failed schema validation: {e}",
            original_error=e
        )
