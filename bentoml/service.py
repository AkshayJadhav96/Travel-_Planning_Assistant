# uv run bentoml serve service:TravelFinanceassistant
import os
import sys

import bentoml
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from loguru import logger
from unified_logging.logging_setup import setup_logging


# Initialize logging before any other imports
setup_logging()
logger.info("Initializing TravelFinanceAssistant service")

with bentoml.importing():
    from llm import initiallize_llm, call_llm



@bentoml.service(workers="cpu_count")
class TravelFinanceassistant:
    def __init__(self) -> None:
        self.agent_executor = initiallize_llm()
        logger.success("LLM executor initialized successfully")

    @bentoml.api
    def query(self, input: str) -> dict:
        """
        Process a user query and return the assistant's response.
        """
        try:
            response = call_llm(input, self.agent_executor)
            # return {"response": response}
            logger.success(f"Successfully processed query. Response length: {len(response)}")
            logger.debug(f"Sample response: {response[:100]}...")  # Log first 100 chars
            
            return {"response": response}
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {"error": f"Error processing query: {str(e)}"}

    @bentoml.api
    def health(self) -> dict:
        """
        Health check endpoint to verify API status.
        """
        try:
            status = {"status": "ok"}
            logger.debug("Health check performed")
            return status
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "error", "details": str(e)}



