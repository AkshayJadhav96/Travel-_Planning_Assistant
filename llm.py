from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent,AgentExecutor
from tools.news import get_news
from tools.Currency import convert_currency
from tools.hotels import search_hotels
from tools.Weather import get_weather
from tools.flights import search_flights
import yaml

model = ChatOllama(
    model="llama3.2"
)

import yaml
from pathlib import Path
# Load config.yaml from the 'tools' directory
config_path = Path(__file__).parent/"tools"/"config.yaml"
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

SYSTEM_PROMPT = config["LLM"]["SYSTEM_PROMPT"]

tools = [get_weather,search_flights,search_hotels,convert_currency,get_news]

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

def initiallize_llm():
   agent = create_tool_calling_agent(model,tools,prompt)
   agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True)
   return agent_executor



def call_llm(query: str, agent_executor: AgentExecutor) -> str:
   response = agent_executor.invoke({'input':query})
   return response['output']

# agent = create_tool_calling_agent(model,tools,prompt)
# agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True)

# res = agent_executor.invoke({'input':"Hi, how are you? Can you tell me,how much is 2 taka  in Indian Rupees?"})
# print(res['output'])
