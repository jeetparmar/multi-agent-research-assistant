import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

from app.core.logging import get_logger
from app.core.config import settings
from app.utils.async_helpers import AsyncLimiter

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
logger = get_logger("llm_service")
llm_limiter = AsyncLimiter(max_concurrent=settings.LLM_MAX_CONCURRENT)


class LLMServiceError(RuntimeError):
    """Raised when the upstream LLM provider cannot fulfill a request."""


class LLMRateLimitError(LLMServiceError):
    """Raised when the upstream LLM provider keeps rate-limiting requests."""


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None

    try:
        return max(float(value), 0.0)
    except ValueError:
        pass

    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None

    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)

    delay = (retry_at - datetime.now(timezone.utc)).total_seconds()
    return max(delay, 0.0)


def _build_backoff_delay(attempt: int, retry_after: str | None) -> float:
    header_delay = _parse_retry_after(retry_after)
    if header_delay is not None:
        return header_delay

    return settings.LLM_RETRY_BASE_DELAY * (2**attempt)


async def call_llm(system_prompt: str, user_prompt: str, request_id: str = "-"):
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        for attempt in range(settings.LLM_MAX_RETRIES + 1):
            try:
                response = await client.post(
                    GROQ_CHAT_COMPLETIONS_URL,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"] or ""
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                is_retryable = status_code in RETRYABLE_STATUS_CODES

                if is_retryable and attempt < settings.LLM_MAX_RETRIES:
                    delay = _build_backoff_delay(
                        attempt, exc.response.headers.get("Retry-After")
                    )
                    logger.warning(
                        "LLM request throttled or unavailable; retrying",
                        extra={
                            "request_id": request_id,
                            "agent": "llm_service",
                            "duration_ms": int(delay * 1000),
                        },
                    )
                    await asyncio.sleep(delay)
                    continue

                if status_code == 429:
                    raise LLMRateLimitError(
                        "Groq rate limit exceeded after retries."
                    ) from exc

                if 500 <= status_code < 600:
                    raise LLMServiceError(
                        f"Groq returned status {status_code} after retries."
                    ) from exc

                raise
            except httpx.RequestError as exc:
                if attempt < settings.LLM_MAX_RETRIES:
                    delay = settings.LLM_RETRY_BASE_DELAY * (2**attempt)
                    logger.warning(
                        "LLM request failed; retrying",
                        extra={
                            "request_id": request_id,
                            "agent": "llm_service",
                            "duration_ms": int(delay * 1000),
                        },
                    )
                    await asyncio.sleep(delay)
                    continue

                raise LLMServiceError("Groq request failed after retries.") from exc
