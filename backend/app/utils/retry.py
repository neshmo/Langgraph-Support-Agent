import time
import logging

logger = logging.getLogger(__name__)


def retry(
    fn,
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
):
    """
    Retry helper with exponential backoff.
    """
    last_exception = None

    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            last_exception = e
            logger.warning(
                f"Retry {attempt + 1}/{retries} failed: {e}"
            )
            time.sleep(delay)
            delay *= backoff

    raise last_exception
