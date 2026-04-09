import httpx
import streamlit as st

from frontend.research_api import (
    DEFAULT_API_BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
    fetch_research,
    normalize_api_base_url,
)

st.set_page_config(
    page_title="Research Assistant",
    layout="wide",
)


def render_subtopics(subtopics: list[str]) -> None:
    st.subheader("Research Plan")
    columns = st.columns(2)
    for index, topic in enumerate(subtopics):
        columns[index % 2].container(border=True).markdown(
            f"**{index + 1}.** {topic}"
        )


def render_report(report: str) -> None:
    st.subheader("Final Report")
    st.container(border=True).markdown(report)


def render_sidebar() -> tuple[str, int]:
    st.sidebar.header("API Settings")
    api_base_url = st.sidebar.text_input(
        "FastAPI base URL",
        value=st.session_state.get("api_base_url", DEFAULT_API_BASE_URL),
        help="The Streamlit frontend sends POST requests to this FastAPI server.",
    )
    timeout_seconds = st.sidebar.number_input(
        "Timeout (seconds)",
        min_value=30,
        max_value=600,
        value=int(DEFAULT_TIMEOUT_SECONDS),
        step=15,
    )
    return api_base_url, timeout_seconds


def main() -> None:
    st.title("Multi-Agent Research Assistant")
    st.caption("Streamlit frontend for the FastAPI `/research` endpoint.")

    api_base_url, timeout_seconds = render_sidebar()

    with st.form("research-form"):
        query = st.text_area(
            "Research topic",
            value=st.session_state.get("last_query", ""),
            placeholder="What are the latest trends in renewable energy?",
            height=160,
        )
        submitted = st.form_submit_button("Run Research", use_container_width=True)

    if submitted:
        st.session_state.pop("last_result", None)
        try:
            normalized_api_base_url = normalize_api_base_url(api_base_url)
            with st.spinner("Calling planner, search, summarizer, and reporter agents..."):
                result = fetch_research(
                    query=query,
                    api_base_url=normalized_api_base_url,
                    timeout_seconds=timeout_seconds,
                )
        except ValueError as exc:
            st.error(str(exc))
        except httpx.HTTPStatusError as exc:
            st.error(
                f"API returned {exc.response.status_code}: "
                f"{exc.response.text[:500] or 'No response body provided.'}"
            )
        except httpx.RequestError as exc:
            st.error(f"Could not reach the API: {exc}")
        else:
            st.session_state["api_base_url"] = normalized_api_base_url
            st.session_state["last_query"] = query.strip()
            st.session_state["last_result"] = result

    result = st.session_state.get("last_result")
    if not result:
        st.info("Start the FastAPI server, enter a topic, and run a research request.")
        return

    st.success(f"Research completed for: {result.query}")
    render_subtopics(result.subtopics)
    render_report(result.report)

    st.download_button(
        label="Download report",
        data=result.report,
        file_name="research_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

    with st.expander("Raw API response"):
        st.json(result.model_dump() if hasattr(result, "model_dump") else result.dict())


if __name__ == "__main__":
    main()
