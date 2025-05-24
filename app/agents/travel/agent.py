from tools import TravelTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.groq import Groq
import os
from dotenv import load_dotenv


tool = TravelTool()

agent = OpenAIAgent.from_tools(tool.to_tool_list(), llm=Groq(model="qwen-qwq-32b", api_key=os.getenv("GROQ_API_KEY")))

response = agent.chat("Search for flights between NYC and PAR on 2025-05-30")

print(response)
