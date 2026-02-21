import time

from app.core.logging import get_logger

# Reporter agent to compile summaries into a final report
logger = get_logger("reporter_agent")

# Reporter agent to compile summaries into a final report
async def report_agent(query: str, summaries: list, request_id: str):
    # Compile the summaries into a structured report format
    report = f"# Research Report\n\n## Topic: {query}\n\n"
    start = time.time()
    try:
        # Add each summary as a section in the report
        for i, summary in enumerate(summaries, 1):
            report += f"### Section {i}\n{summary}\n\n"
        # Log the completion of report generation with timing
        duration = int((time.time() - start) * 1000)
        logger.info(
            "Report generation completed",
            extra={
                "request_id": request_id,
                "agent": "reporter_agent",
                "duration_ms": duration,
            },
        )
        return report
    except Exception as e:
        logger.error(
            f"Report generation failed: {str(e)}",
            extra={
                "request_id": request_id,
                "agent": "reporter_agent",
                "duration_ms": 0,
            },
        )
        raise
