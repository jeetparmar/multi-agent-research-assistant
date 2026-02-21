# Multi-Agent Research Assistant

A FastAPI service that researches a topic using multiple specialized agents:
- `planner`: breaks a query into subtopics
- `search`: gathers web results via Tavily
- `summarizer`: summarizes each subtopic with an LLM
- `reporter`: compiles a final report

## Requirements

- Python 3.10+
- OpenAI API key
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
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Run

Start the API server:

```bash
uvicorn app.main:app --reload
```

API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

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

## Project Structure

```text
app/
  agents/       # Planner, search, summarizer, reporter agents
  services/     # OpenAI and Tavily service clients
  models/       # Request/response models
  middleware/   # Request context middleware
  core/         # Config and logging
  utils/        # Async helpers (retry, limiter)
  main.py       # FastAPI entrypoint
```

## Notes

- Environment variables are loaded from `.env` (`app/core/config.py`).
- The app uses async concurrency for parallel subtopic processing.
