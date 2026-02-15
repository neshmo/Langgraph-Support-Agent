"""
Custom exceptions for LLM and service failures.
Provides structured error handling for OpenRouter API calls.
"""


class LLMError(Exception):
    """Base exception for all LLM-related errors."""
    
    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class LLMRateLimitError(LLMError):
    """Raised when hitting rate limits (HTTP 429)."""
    pass


class LLMAuthError(LLMError):
    """Raised on authentication failures (HTTP 401/403)."""
    pass


class LLMUnavailableError(LLMError):
    """Raised when the LLM service is unavailable (HTTP 404/503)."""
    pass


class LLMResponseParseError(LLMError):
    """Raised when LLM response cannot be parsed as expected."""
    pass
