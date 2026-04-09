# Multi-Agent Research Assistant

A FastAPI service that researches a topic using multiple specialized agents:
- `planner`: breaks a query into subtopics
- `search`: gathers web results via Tavily
- `summarizer`: summarizes each subtopic with an LLM
- `reporter`: compiles a final report

## Requirements

- Python 3.10+
- Groq API key
- Tavily API key

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
TAVILY_API_KEY=your_tavily_api_key
API_BASE_URL=http://127.0.0.1:8000
LLM_MAX_CONCURRENT=2
LLM_MAX_RETRIES=3
LLM_RETRY_BASE_DELAY=1.0
LLM_TIMEOUT_SECONDS=60
```

## Run

Start the API server:

```bash
uvicorn app.main:app --reload
```

Start the Streamlit frontend in a second terminal:

```bash
streamlit run streamlit_app.py
```

API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Streamlit UI: `http://127.0.0.1:8501`

## Usage

Send a research request:

```bash
curl -X POST "http://127.0.0.1:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the latest trends in renewable energy?"}'
```

Example response shape:

```json
{
  "query": "What are the latest trends in renewable energy?",
  "subtopics": ["..."],
  "report": "# Research Report\n..."
}
```

Or use the Streamlit UI:

- Enter a topic in the text area.
- Confirm the FastAPI base URL in the sidebar.
- Click `Run Research` to call `POST /research`.
- Review the generated subtopics and final markdown report.

## Project Structure

```text
app/
  agents/       # Planner, search, summarizer, reporter agents
  services/     # Groq and Tavily service clients
  models/       # Request/response models
  middleware/   # Request context middleware
  core/         # Config and logging
  utils/        # Async helpers (retry, limiter)
  main.py       # FastAPI entrypoint
frontend/
  research_api.py  # Shared client used by the Streamlit frontend
streamlit_app.py   # Streamlit frontend
```

## Notes

- Environment variables are loaded from `.env` by both the backend config and the Streamlit API client.
- `GROQ_MODEL` is optional; if omitted, the app uses `llama-3.3-70b-versatile`.
- The app uses async concurrency for parallel subtopic processing, with a shared limiter for Groq calls.
- Groq `429` and transient `5xx` responses are retried with backoff before the API returns a `503` or `502`.
