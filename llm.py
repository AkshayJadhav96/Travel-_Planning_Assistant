"""Language model utilities for Travel and Finance Assistant."""

from pathlib import Path

import yaml
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from tools.currency import convert_currency
from tools.flights import search_flights
from tools.hotels import search_hotels
from tools.news import get_news
from tools.weather import get_weather

model = ChatOllama(model="qwen2.5:7b")

# Load config.yaml from the 'tools' directory
config_path = Path(__file__).parent / "tools" / "config.yaml"
with config_path.open() as file:
    config = yaml.safe_load(file)

SYSTEM_PROMPT = config["LLM"]["SYSTEM_PROMPT"]

tools = [get_weather, search_flights, search_hotels, convert_currency, get_news]

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])


def initiallize_llm() -> AgentExecutor:
    """Initialize the LLM agent executor with tools and prompt."""
    agent = create_tool_calling_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def call_llm(query: str, agent_executor: AgentExecutor) -> str:
    """Call the LLM with a query and return the response."""
    response = agent_executor.invoke({"input": query})
    return response["output"]
