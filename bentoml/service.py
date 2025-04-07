"""Travel and Finance Assistant service module."""

import sys
from pathlib import Path

from loguru import logger

import bentoml

sys.path.append(str(Path(__file__).parent.parent.resolve()))
from unified_logging.logging_setup import setup_logging

# Initialize logging before any other imports
setup_logging()
logger.info("Initializing TravelFinanceAssistant service")

with bentoml.importing():
    from llm import call_llm, initiallize_llm


@bentoml.service(workers="cpu_count")
class TravelFinanceassistant:
    """Service class for Travel and Finance Assistant."""

    def __init__(self) -> None:
        """Initialize the LLM executor."""
        self.agent_executor = initiallize_llm()
        logger.success("LLM executor initialized successfully")

    @bentoml.api
    def query(self, user_input: str) -> dict:
        """Process a user query and return the assistant's response."""
        try:
            response = call_llm(user_input, self.agent_executor)
            logger.success(
                f"Successfully processed query. Response length: {len(response)}",
            )
            logger.debug(f"Sample response: {response[:100]}...")  # Log first 100 chars
        except ValueError as e:
            logger.error(f"Error processing query: {e!s}")
            return {"error": f"Error processing query: {e!s}"}
        else:
            return {"response": response}

    @bentoml.api
    def health(self) -> dict:
        """Health check endpoint to verify API status."""
        try:
            status = {"status": "ok"}
            logger.debug("Health check performed")
        except ValueError as e:
            logger.error(f"Health check failed: {e!s}")
            return {"status": "error", "details": str(e)}
        else:
            return status
