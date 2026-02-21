import httpx
from app.core.config import settings

TAVILY_URL = "https://api.tavily.com/search"

# Function to perform web search using Tavily API
async def tavily_search(query: str, max_results: int = 5):
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": False,
    }
    # Make an asynchronous POST request to the Tavily API with a timeout of 30 seconds
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(TAVILY_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
    # Extract relevant information from the API response and return it in a structured format
    results = []
    for item in data.get("results", []):
        # Each search result includes the title, URL, and content snippet for the relevant web page
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
            }
        )

    return results
