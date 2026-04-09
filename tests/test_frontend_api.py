import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from app.models.research_models import ResearchResponse
from frontend.research_api import (
    build_how_it_works_url,
    build_research_url,
    fetch_research,
    normalize_api_base_url,
    parse_research_response,
)


class ResearchApiClientTests(unittest.TestCase):
    def test_normalize_api_base_url_strips_whitespace_and_trailing_slash(self):
        self.assertEqual(
            normalize_api_base_url(" http://127.0.0.1:8000/ "),
            "http://127.0.0.1:8000",
        )

    def test_build_research_url_appends_endpoint(self):
        self.assertEqual(
            build_research_url("http://127.0.0.1:8000/"),
            "http://127.0.0.1:8000/research",
        )

    def test_build_how_it_works_url_appends_endpoint(self):
        self.assertEqual(
            build_how_it_works_url("http://127.0.0.1:8000/"),
            "http://127.0.0.1:8000/how-it-works",
        )

    def test_parse_research_response_validates_shape(self):
        with self.assertRaises(ValidationError):
            parse_research_response({"query": "AI", "subtopics": "invalid"})

    def test_fetch_research_posts_expected_payload(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "query": "AI agents",
            "subtopics": ["planning", "tool use"],
            "report": "# Research Report",
        }

        with patch(
            "frontend.research_api.httpx.post",
            return_value=mock_response,
        ) as post:
            result = fetch_research(
                "  AI agents  ",
                api_base_url="http://127.0.0.1:8000/",
                timeout_seconds=45,
            )

        post.assert_called_once_with(
            "http://127.0.0.1:8000/research",
            json={"query": "AI agents"},
            timeout=45,
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertIsInstance(result, ResearchResponse)
        self.assertEqual(result.subtopics, ["planning", "tool use"])

    def test_fetch_research_rejects_blank_query(self):
        with self.assertRaises(ValueError):
            fetch_research("   ")
