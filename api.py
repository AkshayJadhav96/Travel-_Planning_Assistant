from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm import initiallize_llm, call_llm

# Initialize FastAPI app
app = FastAPI(title="Travel and Finance Assistant API")

# Initialize LLM once
agent_executor = initiallize_llm()

# Define the request model
class Query(BaseModel):
    input: str

# Define the query endpoint
@app.post("/query")
def query_assistant(query: Query):
    """
    Process a user query and return the assistant's response.
    """
    try:
        response = call_llm(query.input, agent_executor)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Optional health check endpoint
@app.get("/health")
def health_check():
    """
    Check if the API is running.
    """
    return {"status": "ok"}

# Run the API (for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
