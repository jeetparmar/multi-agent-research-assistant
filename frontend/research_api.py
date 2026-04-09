import os

import httpx
from dotenv import load_dotenv

from app.models.research_models import ResearchResponse

load_dotenv()

DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "120"))


def normalize_api_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if not normalized:
        raise ValueError("API base URL is required.")
    return normalized


def build_research_url(base_url: str) -> str:
    return f"{normalize_api_base_url(base_url)}/research"


def build_how_it_works_url(base_url: str) -> str:
    return f"{normalize_api_base_url(base_url)}/how-it-works"


def parse_research_response(payload: dict) -> ResearchResponse:
    return ResearchResponse(**payload)


def fetch_research(
    query: str,
    api_base_url: str = DEFAULT_API_BASE_URL,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> ResearchResponse:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("Enter a research query before submitting.")

    response = httpx.post(
        build_research_url(api_base_url),
        json={"query": cleaned_query},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return parse_research_response(response.json())
