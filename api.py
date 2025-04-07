"""Travel and Finance Assistant API module."""

from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel

from llm import call_llm, initiallize_llm
from unified_logging.logging_setup import setup_logging

setup_logging()
logger.info("Initializing Travel and Finance Assistant API")

# Initialize FastAPI app
app = FastAPI(title="Travel and Finance Assistant API")

# Initialize LLM once
agent_executor = initiallize_llm()


# Define the request model
class Query(BaseModel):
    """Request model for user queries."""

    input: str


# Define the query endpoint
@app.post("/query")
def query_assistant(query: Query) -> dict[str, str]:
    """Process a user query and return the assistant's response."""
    try:
        response = call_llm(query.input, agent_executor)
        logger.success("response: ", response)
    except ValueError as e:
        logger.error(f"Request failed: {e!s}")
        raise HTTPException(
            status_code=500, detail=f"Error processing query: {e!s}",
        ) from e
    else:
        return {"response": response}


# Optional health check endpoint
@app.get("/health")
def health_check() -> dict[str, str]:
    """Check if the API is running."""
    return {"status": "ok"}


# Run the API (for development)
if __name__ == "__main__":
    import uvicorn
    # Consider changing host to "127.0.0.1" for local development instead of "0.0.0.0"
    uvicorn.run(app, host="127.0.0.1", port=8000)
