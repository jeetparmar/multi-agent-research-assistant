import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


# Configuration class to load API keys from environment variables
class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    LLM_MAX_CONCURRENT = _get_int("LLM_MAX_CONCURRENT", 2)
    LLM_MAX_RETRIES = _get_int("LLM_MAX_RETRIES", 3)
    LLM_RETRY_BASE_DELAY = _get_float("LLM_RETRY_BASE_DELAY", 1.0)
    LLM_TIMEOUT_SECONDS = _get_float("LLM_TIMEOUT_SECONDS", 60.0)

settings = Settings()
