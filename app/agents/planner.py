import json
import time
from json import JSONDecodeError

from app.core.logging import get_logger
from app.services.llm_service import call_llm, llm_limiter
logger = get_logger("planner_agent")


def _parse_plan_response(response: str) -> dict:
    cleaned = response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        plan = json.loads(cleaned)
    except JSONDecodeError as exc:
        raise ValueError(f"Planner returned invalid JSON: {response!r}") from exc

    subtopics = plan.get("subtopics")
    if not isinstance(subtopics, list) or not all(
        isinstance(topic, str) and topic.strip() for topic in subtopics
    ):
        raise ValueError(f"Planner returned invalid subtopics payload: {plan!r}")

    return {"subtopics": [topic.strip() for topic in subtopics]}

# Planner agent to break down research topic into subtopics
async def planner_agent(query: str, request_id: str):
    system_prompt = "You are a research planner."
    user_prompt = f"""
        Break the following research topic into 3-5 subtopics in JSON format:
        Topic: {query}

        Output format:
        {{
            "subtopics": ["...", "..."]
        }}
    """
    start = time.time()
    try:
        # Call the LLM with rate limiting to get the research plan
        response = await llm_limiter.run(
            call_llm(system_prompt, user_prompt, request_id)
        )
        plan = _parse_plan_response(response)
        duration = int((time.time() - start) * 1000)
        logger.info(
            "Planning completed",
            extra={
                "request_id": request_id,
                "agent": "planner_agent",
                "duration_ms": duration,
            },
        )
        return plan
    except Exception as e:
        logger.error(
            f"Planning failed: {str(e)}",
            extra={
                "request_id": request_id,
                "agent": "planner_agent",
                "duration_ms": 0,
            },
        )
        raise
