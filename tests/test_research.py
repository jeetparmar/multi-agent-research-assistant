import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.agents.planner import planner_agent
from app.main import app


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


class ResearchEndpointTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
