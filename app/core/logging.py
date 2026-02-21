import logging
import sys
from pythonjsonlogger import jsonlogger

# Set up structured logging with JSON format
def setup_logging():
    # Get the root logger and configure it to output JSON logs to stdout
    logger = logging.getLogger()
    # Set the logging level to INFO (can be adjusted to DEBUG for more verbose output)
    logger.setLevel(logging.INFO)
    # Create a stream handler that outputs to stdout
    log_handler = logging.StreamHandler(sys.stdout)
    # Define a JSON formatter that includes relevant fields for structured logging
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(agent)s %(duration_ms)s"
    )
    # Set the formatter for the log handler and add it to the logger
    log_handler.setFormatter(formatter)
    # Clear existing handlers and add the new JSON log handler
    logger.handlers = [log_handler]

# Call the setup function to initialize logging configuration
def get_logger(name: str):
    return logging.getLogger(name)
