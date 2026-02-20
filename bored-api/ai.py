import asyncio
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import FunctionAgent
from bored_api import pr
from dotenv import load_dotenv
import os
from tools import get_tools
from proxy_mgmt.proxy import BoardProxy

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
    try:
        response = await agent.run(user_input)
    except Exception as e:
        print(f"Error querying agent: {e}")
        response = None
    return response

async def review_pr_and_return_set_of_tickets(pr_url: str) -> str | None:
    system_prompt = f"""
    You are a helpful assistant that reviews a GitHub PR and returns a list of possible issue IDs that might be related.
    Please provide your response in the following format:
    <issue_id_1>, <issue_id_2>, ...
    Say "None" if there are no linked open issues.
    You have access to the following tools:
    """
    for tool in get_tools():
        system_prompt += f"- {tool.__name__}\n"
    system_prompt += f"You can also use the following board proxy methods to get information about tickets:\n"

    
    user_input = f"Review the PR at {pr_url} and return a list of issues"
    response = await query_agent(get_tools(), system_prompt, user_input)
    return response

if __name__ == "__main__":
    response = asyncio.run(review_pr_and_return_set_of_tickets("https://github.com/your-repo/your-pr"))
    print(response)
