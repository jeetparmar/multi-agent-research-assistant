from fastapi import FastAPI, Request
import asyncio

from app.middleware.request_context import RequestContextMiddleware
from app.models.research_models import ResearchRequest
from app.agents.planner import planner_agent
from app.agents.search import search_agent
from app.agents.summarizer import summarize_agent
from app.agents.reporter import report_agent

# Initialize FastAPI app and add middleware for request context
app = FastAPI(title="Multi-Agent Research Assistant", version="1.0", description="An AI assistant that performs research tasks using multiple agents.", contact={"name": "Support", "email": "support@example.com"}, license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"}, docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")
# Add request context middleware to track request_id and timing
app.add_middleware(RequestContextMiddleware)

# Helper function to process each subtopic
async def process_topic(topic: str, request_id: str):
    # Step 1: Search for the subtopic
    search_results = await search_agent(topic, request_id)
    # Step 2: Combine search results and summarize
    combined_content = " ".join([item["content"] for item in search_results])
    # Step 3: Summarize the combined content
    summary = await summarize_agent(combined_content, request_id)
    return summary

# API endpoint for research
# Request body example:
# {
#   "query": "What are the latest trends in renewable energy?"
# }
@app.post("/research")
async def research(request: ResearchRequest, req: Request):
    # Extract request_id from middleware context
    request_id = req.state.request_id
    # Step 1: Generate research plan with subtopics
    plan = await planner_agent(request.query, request_id)
    # Step 2: For each subtopic, perform search and summarization in parallel
    tasks = [process_topic(topic, request_id) for topic in plan["subtopics"]]
    # Wait for all tasks to complete and gather summaries
    summaries = await asyncio.gather(*tasks)
    # Step 3: Compile final report from summaries
    final_report = await report_agent(request.query, summaries, request_id)
    # Return the structured response
    return {
        "query": request.query,
        "subtopics": plan["subtopics"],
        "report": final_report,
    }
