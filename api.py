from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools.news import get_news
from tools.Currency import convert_currency
from tools.flights import search_flights
from tools.hotels import search_hotels
from tools.Weather import get_weather

# Initialize the Llama 3.2 model with Ollama
model = ChatOllama(model="llama3.2")

# Define the system prompt
SYSTEM_PROMPT = """You are a highly capable travel and finance assistant. Your capabilities include:
1. Weather Forecasting: You can provide detailed weather forecasts for any city worldwide for up to 14 days.
   - Use the get_weather tool with city name and optional days parameter.

2. Flight Search: You can search for flights between airports worldwide.
   - Use the search_flights tool with source (IATA code), destination (IATA code), date (YYYY-MM-DD), and optional parameters like adults and currency (ISO 4217).
   - Always verify airport codes before searching.

3. Hotel Search: You can find hotels in any city with various filters.
   - Use the search_hotels tool with city code (IATA e.g. NYC), radius (in KM or MI), amenities as string of comma separated amenities (e.g. "pool,spa,wifi"), ratings as string of comma separated ratings (e.g. "2,3,4").

4. Currency Conversion: You can convert between any currencies with live exchange rates.
   - Use the convert_currency tool with amount, from_currency (ISO 4217), and to_currency (ISO 4217).
   - Use standard 3-letter currency codes.
   - This tool will directly convert the given amount from one currency to another; you just need to call it.

General Guidelines:
- Always use tools when precise information is requested.
- For flight/hotel searches, ask for clarification if parameters are unclear.
- Present results in a clear, organized manner.
- When using tools, handle errors gracefully and explain them to the user.
- Be concise but thorough in your responses.
- If a tool is giving input type errors or formatting errors, correct it and retry calling it again for at least 2 times and max 4 times."""

# Define the tools
tools = [get_weather, search_flights, search_hotels, convert_currency, get_news]

# Set up the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create the agent and executor
agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Initialize FastAPI app
app = FastAPI(title="Travel and Finance Assistant API")

# Define the request model
class Query(BaseModel):
    input: str

# Define the query endpoint
@app.post("/query")
def query_assistant(query: Query):
    """
    Process a user query and return the assistant's response.
    
    Args:
        query (Query): A Pydantic model containing the user's input string.
    
    Returns:
        dict: A JSON response with the assistant's output.
    
    Raises:
        HTTPException: If an error occurs during processing, returns a 500 status code.
    """
    try:
        res = agent_executor.invoke({'input': query.input})
        return {"response": res['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Optional health check endpoint
@app.get("/health")
def health_check():
    """
    Check if the API is running.
    
    Returns:
        dict: A simple status message.
    """
    return {"status": "ok"}

# Run the API (for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)