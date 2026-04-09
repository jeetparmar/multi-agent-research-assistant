import asyncio
import inspect
import textwrap
from html import escape

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.agents.planner import planner_agent
from app.agents.reporter import report_agent
from app.agents.search import search_agent
from app.agents.summarizer import summarize_agent
from app.middleware.request_context import RequestContextMiddleware
from app.models.research_models import ResearchRequest, ResearchResponse
from app.services.llm_service import LLMRateLimitError, LLMServiceError

app = FastAPI(
    title="Multi-Agent Research Assistant",
    version="1.0",
    description="An AI assistant that performs research tasks using multiple agents.",
    contact={"name": "Support", "email": "support@example.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.add_middleware(RequestContextMiddleware)


async def process_topic(topic: str, request_id: str):
    search_results = await search_agent(topic, request_id)
    combined_content = " ".join(item["content"] for item in search_results)
    summary = await summarize_agent(combined_content, request_id)
    return summary


def _build_pipeline_code_example() -> str:
    snippets = [
        textwrap.dedent(inspect.getsource(process_topic)).strip(),
        textwrap.dedent(inspect.getsource(research)).strip(),
    ]
    return "\n\n".join(snippets)


def build_how_it_works_html() -> str:
    code_example = escape(_build_pipeline_code_example())
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>How Multi-Agent Research Works</title>
            <style>
                :root {{
                    color-scheme: light;
                    --bg: #f6f4ef;
                    --panel: #fffdf8;
                    --text: #1c1a17;
                    --muted: #5a564f;
                    --accent: #0f766e;
                    --border: #d8d1c6;
                    --code-bg: #1f2937;
                    --code-text: #f9fafb;
                }}

                * {{
                    box-sizing: border-box;
                }}

                body {{
                    margin: 0;
                    font-family: "Iowan Old Style", "Palatino Linotype", serif;
                    background:
                        radial-gradient(circle at top right, #d7efe7 0, transparent 28%),
                        linear-gradient(180deg, #f9f7f2 0%, var(--bg) 100%);
                    color: var(--text);
                    line-height: 1.6;
                }}

                main {{
                    max-width: 960px;
                    margin: 0 auto;
                    padding: 48px 24px 80px;
                }}

                .hero,
                .panel {{
                    background: rgba(255, 253, 248, 0.95);
                    border: 1px solid var(--border);
                    border-radius: 20px;
                    box-shadow: 0 18px 48px rgba(28, 26, 23, 0.08);
                }}

                .hero {{
                    padding: 32px;
                    margin-bottom: 24px;
                }}

                .panel {{
                    padding: 28px 32px;
                    margin-bottom: 20px;
                }}

                h1,
                h2 {{
                    margin-top: 0;
                    font-family: "Avenir Next", "Segoe UI", sans-serif;
                    letter-spacing: -0.03em;
                }}

                h1 {{
                    font-size: clamp(2rem, 5vw, 3.4rem);
                    margin-bottom: 12px;
                }}

                h2 {{
                    font-size: 1.35rem;
                    margin-bottom: 14px;
                }}

                p,
                li {{
                    font-size: 1.02rem;
                }}

                .eyebrow {{
                    color: var(--accent);
                    font-family: "Avenir Next", "Segoe UI", sans-serif;
                    font-size: 0.9rem;
                    font-weight: 700;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                }}

                ol,
                ul {{
                    padding-left: 1.2rem;
                    margin: 0;
                }}

                code.inline {{
                    background: rgba(15, 118, 110, 0.08);
                    border-radius: 6px;
                    padding: 0.1rem 0.35rem;
                    font-family: "SFMono-Regular", "Menlo", monospace;
                    font-size: 0.92rem;
                }}

                pre {{
                    margin: 0;
                    padding: 22px;
                    overflow-x: auto;
                    border-radius: 16px;
                    background: var(--code-bg);
                    color: var(--code-text);
                    font-size: 0.92rem;
                    line-height: 1.5;
                }}
            </style>
        </head>
        <body>
            <main>
                <section class="hero">
                    <div class="eyebrow">System Walkthrough</div>
                    <h1>How this research assistant works</h1>
                    <p>
                        This app uses a Streamlit frontend to collect a topic, a FastAPI backend to orchestrate the work,
                        Tavily to fetch web results, and the LLM service to plan and summarize. The backend keeps a
                        request id on each call so logs for the planner, search, summarizer, and reporter stay tied to
                        the same request.
                    </p>
                </section>

                <section class="panel">
                    <h2>Detailed flow</h2>
                    <ol>
                        <li>
                            The Streamlit UI sends a <code class="inline">POST /research</code> request with the user query.
                        </li>
                        <li>
                            <code class="inline">planner_agent</code> asks the LLM to break the topic into 3 to 5 subtopics.
                        </li>
                        <li>
                            The backend starts one <code class="inline">process_topic(...)</code> task per subtopic and runs
                            them together with <code class="inline">asyncio.gather(...)</code>.
                        </li>
                        <li>
                            Inside each task, <code class="inline">search_agent</code> calls Tavily with retry logic, then
                            filters out weak results whose content is too short to summarize reliably.
                        </li>
                        <li>
                            The remaining search snippets are merged into one text block and passed to
                            <code class="inline">summarize_agent</code>, which asks the LLM for key insights, statistics,
                            risks, and opportunities.
                        </li>
                        <li>
                            After every subtopic summary returns, <code class="inline">report_agent</code> stitches them into
                            one markdown report and the API returns the final payload to Streamlit.
                        </li>
                    </ol>
                </section>

                <section class="panel">
                    <h2>Important implementation details</h2>
                    <ul>
                        <li>
                            LLM calls pass through a shared limiter so concurrent subtopic work does not flood the model provider.
                        </li>
                        <li>
                            Rate limit failures are mapped to HTTP 503 and temporary provider failures are mapped to HTTP 502.
                        </li>
                        <li>
                            The reporter is intentionally simple: it formats the subtopic summaries into markdown instead of
                            asking the model for one more synthesis pass.
                        </li>
                    </ul>
                </section>

                <section class="panel">
                    <h2>Code example</h2>
                    <p>
                        The key orchestration lives in the FastAPI entrypoint below. The first function handles one subtopic.
                        The second function runs the full request pipeline.
                    </p>
                    <pre><code>{code_example}</code></pre>
                </section>
            </main>
        </body>
        </html>
        """
    )


@app.get("/how-it-works", response_class=HTMLResponse, include_in_schema=False)
async def how_it_works() -> HTMLResponse:
    return HTMLResponse(build_how_it_works_html())


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest, req: Request):
    request_id = req.state.request_id
    try:
        plan = await planner_agent(request.query, request_id)
        tasks = [process_topic(topic, request_id) for topic in plan["subtopics"]]
        summaries = await asyncio.gather(*tasks)
        final_report = await report_agent(request.query, summaries, request_id)
        return {
            "query": request.query,
            "subtopics": plan["subtopics"],
            "report": final_report,
        }
    except LLMRateLimitError as exc:
        raise HTTPException(
            status_code=503,
            detail="The language model provider is rate-limiting requests. Please retry shortly.",
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail="The language model provider is temporarily unavailable. Please retry shortly.",
        ) from exc
