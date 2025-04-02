# uv run bentoml serve service:TravelFinanceassistant
import os
import sys

import bentoml
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

with bentoml.importing():
    from llm import initiallize_llm, call_llm



@bentoml.service(workers="cpu_count")
class TravelFinanceassistant:
    def __init__(self) -> None:
        self.agent_executor = initiallize_llm()

    @bentoml.api
    def query(self, input: str) -> dict:
        """
        Process a user query and return the assistant's response.
        """
        try:
            response = call_llm(input, self.agent_executor)
            return {"response": response}
        except Exception as e:
            return {"error": f"Error processing query: {str(e)}"}

    @bentoml.api
    def health(self) -> dict:
        """
        Health check endpoint to verify API status.
        """
        return {"status": "ok"}



