import asyncio
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import FunctionAgent
from dotenv import load_dotenv
import os
from tools import get_tools

load_dotenv()

system_prompt = """
You are a helpful assistant that interacts with GitHub issues and sends simple responses.
Your job is to use the tools provided to you to get information about GitHub issues and their statuses.
You have access to the following tools:
"""

for tool in get_tools():
    system_prompt += f"- {tool.__name__}\n"

async def main():
    agent = FunctionAgent(
        llm=GoogleGenAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash"),
        tools=get_tools(),
        system_prompt=system_prompt,
    )
    user_input = "What are the current open issues on GitHub?"
    response = await agent.run(user_input)
    print(response)

async def query_agent(tools: list[function], system_prompt: str, user_input: str):
    agent = FunctionAgent(
        llm=GoogleGenAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash"),
        tools=tools,
        system_prompt=system_prompt,
    )
    response = await agent.run(user_input)
    return response

if __name__ == "__main__":
    asyncio.run(main())
