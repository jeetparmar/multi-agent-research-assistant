from app.services.llm_service import call_llm
import json
from app.utils.async_helpers import AsyncLimiter

# Initialize an async limiter to control the number of concurrent LLM calls
llm_limiter = AsyncLimiter(max_concurrent=3)

# Planner agent to break down research topic into subtopics
async def planner_agent(query: str):
    system_prompt = "You are a research planner."
    user_prompt = f"""
        Break the following research topic into 3-5 subtopics in JSON format:
        Topic: {query}

        Output format:
        {{
            "subtopics": ["...", "..."]
        }}
    """
    # Call the LLM with rate limiting to get the research plan
    response = await llm_limiter.run(call_llm(system_prompt, user_prompt))
    return json.loads(response)
