import time

from app.core.logging import get_logger
from app.services.web_search_service import tavily_search
from app.utils.async_helpers import retry_async

# Initialize the logger for the search agent
logger = get_logger("search_agent")

# Search agent that uses Tavily API to perform web search based on the research topic. It includes retry logic and filters results to ensure quality content for summarization.
async def search_agent(topic: str, request_id: str):
    start = time.time()
    try:
        # Perform web search with retry logic   
        results = await retry_async(tavily_search, 3, 1, topic)
        # Filter results to ensure they have sufficient content for summarization
        filtered = [r for r in results if r["content"] and len(r["content"]) > 200]
        # Log search completion with duration and number of results
        duration = int((time.time() - start) * 1000)
        logger.info(
            "Search completed",
            extra={
                "request_id": request_id,
                "agent": "search_agent",
                "duration_ms": duration,
            },
        )
        return filtered
    except Exception as e:
        logger.error(
            f"Search failed: {str(e)}",
            extra={
                "request_id": request_id,
                "agent": "search_agent",
                "duration_ms": 0,
            },
        )
        raise
