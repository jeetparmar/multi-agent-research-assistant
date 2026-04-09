import unittest
from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from app.agents.planner import planner_agent
from app.core.config import settings
from app.main import app
from app.services.llm_service import (
    GROQ_CHAT_COMPLETIONS_URL,
    LLMRateLimitError,
    call_llm,
)


class _FakeAsyncClient:
    def __init__(self, responses):
        self.post = AsyncMock(side_effect=responses)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


def _make_response(status_code, payload, headers=None):
    request = httpx.Request("POST", GROQ_CHAT_COMPLETIONS_URL)
    return httpx.Response(
        status_code,
        json=payload,
        headers=headers or {},
        request=request,
    )


class PlannerAgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_planner_agent_accepts_request_id(self):
        with patch(
            "app.agents.planner.call_llm",
            new=AsyncMock(return_value='{"subtopics": ["solar", "storage"]}'),
        ):
            plan = await planner_agent("renewable energy", "req-123")

        self.assertEqual(plan, {"subtopics": ["solar", "storage"]})

    async def test_planner_agent_parses_fenced_json(self):
        with patch(
            "app.agents.planner.call_llm",
            new=AsyncMock(
                return_value='```json\n{"subtopics": ["solar", "storage"]}\n```'
            ),
        ):
            plan = await planner_agent("renewable energy", "req-456")

        self.assertEqual(plan, {"subtopics": ["solar", "storage"]})


class LlmServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_call_llm_retries_after_rate_limit_and_returns_content(self):
        fake_client = _FakeAsyncClient(
            [
                _make_response(
                    429,
                    {"error": {"message": "rate limited"}},
                    headers={"Retry-After": "0"},
                ),
                _make_response(
                    200,
                    {
                        "choices": [
                            {"message": {"content": "Recovered summary"}}
                        ]
                    },
                ),
            ]
        )

        with (
            patch("app.services.llm_service.httpx.AsyncClient", return_value=fake_client),
            patch("app.services.llm_service.asyncio.sleep", new=AsyncMock()) as sleep,
            patch.object(settings, "LLM_MAX_RETRIES", 1),
        ):
            result = await call_llm("system", "user", "req-1")

        self.assertEqual(result, "Recovered summary")
        self.assertEqual(fake_client.post.await_count, 2)
        sleep.assert_awaited_once_with(0.0)


class ResearchEndpointTests(unittest.TestCase):
    def test_how_it_works_page_returns_html_with_flow_and_code_example(self):
        client = TestClient(app)
        response = client.get("/how-it-works")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("How this research assistant works", response.text)
        self.assertIn("Detailed flow", response.text)
        self.assertIn("Code example", response.text)
        self.assertIn("async def process_topic", response.text)
        self.assertIn("async def research", response.text)

    def test_research_endpoint_passes_request_id_through_pipeline(self):
        query = "What are the latest trends in renewable energy?"
        planner = AsyncMock(return_value={"subtopics": ["solar", "storage"]})
        process_topic = AsyncMock(side_effect=["summary 1", "summary 2"])
        reporter = AsyncMock(return_value="# Research Report")

        with (
            patch("app.main.planner_agent", new=planner),
            patch("app.main.process_topic", new=process_topic),
            patch("app.main.report_agent", new=reporter),
        ):
            client = TestClient(app)
            response = client.post("/research", json={"query": query})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "query": query,
                "subtopics": ["solar", "storage"],
                "report": "# Research Report",
            },
        )

        request_id = planner.await_args.args[1]
        self.assertTrue(request_id)
        self.assertEqual(planner.await_args.args[0], query)
        self.assertEqual(
            [call.args[0] for call in process_topic.await_args_list],
            ["solar", "storage"],
        )
        self.assertTrue(
            all(call.args[1] == request_id for call in process_topic.await_args_list)
        )
        reporter.assert_awaited_once_with(query, ["summary 1", "summary 2"], request_id)

    def test_research_endpoint_returns_503_when_llm_rate_limited(self):
        query = "What are the latest trends in renewable energy?"

        with patch(
            "app.main.planner_agent",
            new=AsyncMock(side_effect=LLMRateLimitError("rate limited")),
        ):
            client = TestClient(app)
            response = client.post("/research", json={"query": query})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "detail": "The language model provider is rate-limiting requests. Please retry shortly."
            },
        )


if __name__ == "__main__":
    unittest.main()
