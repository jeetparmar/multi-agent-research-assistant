import time
from app.core.logging import get_logger
from app.services.llm_service import call_llm, llm_limiter

# Initialize the logger for the summarizer agent
logger = get_logger("summarizer_agent")

# Summarizer agent that takes research content and produces a structured summary with key insights, statistics, risks, and opportunities.
async def summarize_agent(content: str, request_id: str):
    system_prompt = "You are a professional research analyst."
    user_prompt = f"""
    Summarize the following research content:

    {content}

    Provide:
    - Key Insights
    - Statistics
    - Risks
    - Opportunities
    """
    
    start = time.time()
    try:
        # Use the LLM to generate a summary based on the provided content and prompts
        summary = await llm_limiter.run(
            call_llm(system_prompt, user_prompt, request_id)
        )
        duration = int((time.time() - start) * 1000)
        logger.info(
            f"Summarization completed",
            extra={
                "request_id": request_id,
                "agent": "summarizer_agent",
                "duration_ms": duration,
            },
        )
        return summary
    except Exception as e:
        logger.error(
            f"Summarization failed: {str(e)}",
            extra={
                "request_id": request_id,
                "agent": "summarizer_agent",
                "duration_ms": 0,
            },
        )
        raise
