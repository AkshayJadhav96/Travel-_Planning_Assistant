from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent,AgentExecutor
from tools.news import get_news
from tools.Currency import convert_currency
from tools.flights import search_flights
from tools.hotels import search_hotels
from tools.Weather import get_weather

model = ChatOllama(
    model="llama3.2"
)

SYSTEM_PROMPT = """You are a highly capable travel and finance assistant. Your capabilities include:
1. Weather Forecasting: You can provide detailed weather forecasts for any city worldwide for up to 14 days.
   - Use the get_weather tool with city name and optional days parameter.

2. Flight Search: You can search for flights between airports worldwide.
   - Use the search_flights tool with source (IATA code), destination (IATA code), date (YYYY-MM-DD), and optional parameters like adults and currency (ISO 4217).
   - Always verify airport codes before searching.

3. Hotel Search: You can find hotels in any city with various filters.
   - Use the search_hotels tool with city code (IATA e.g. NYC), radius (in KM or MI),amenities as string of comma separated ammenities(e.g."pool,spa,wifi"),ratings as string of comma separated ratings (e.g. "2,3,4").

4. Currency Conversion: You can convert between any currencies with live exchange rates.
   - Use the convert_currency tool with amount, from_currency(ISO 4217), and to_currency(ISO 4217).
   - Use standard 3-letter currency codes.
   - This tool will direct convert the given amount from one currency to other you just need to call it.

General Guidelines:
- Always use tools when precise information is requested.
- For flight/hotel searches, ask for clarification if parameters are unclear.
- Present results in a clear, organized manner.
- When using tools, handle errors gracefully and explain them to the user.
- Be concise but thorough in your responses.
- If tool is giving some input type errors or fromatting errors, correct it and retry calling it again for atleast 2 times and max 4 times"""

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
