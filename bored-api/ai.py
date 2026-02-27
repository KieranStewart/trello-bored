import asyncio
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import FunctionAgent
from bored_api import pr
from dotenv import load_dotenv
import os
from proxy_mgmt.proxy import BoardProxy
from tools import get_tools, get_ticket, get_all_tickets, get_all_labels, get_all_prs, get_pr

from proxy_mgmt.implementations.github_projects import Ticket, Label

load_dotenv()

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

async def review_ticket_and_get_labels(ticket_id: int) -> str | None:
    tickets = get_all_tickets()
    # print(tickets)
    ticket_ids = [ticket.number for ticket in tickets]
    if ticket_id not in ticket_ids:
        raise ValueError(f"Ticket ID {ticket_id} not found in board")
    ticket: Ticket = tickets[ticket_ids.index(ticket_id)]
    system_prompt = f"""
    You are a helpful assistant that reviews a GitHub issue and generates a list of relevant labels based on the content of the issue.
    Please provide your response in the following format:
    <label_1>, <label_2>, ...
    Say "N/A" if there are no relevant labels. Please only return existing labels that are relevant to the issue, do not make up new labels.
    You have access to the following tools:
    """
    for tool in get_tools():
        system_prompt += f"- {tool.__name__}\n"
    
    user_input = f"Review issue {ticket.item_id} and generate a list of relevant labels"
    response = await query_agent(get_tools(), system_prompt, user_input)
    return response

async def review_pr_and_get_labels(pr_number: int) -> str | None:
    prs = get_all_prs()
    pr_numbers = [pr.number for pr in prs]
    if pr_number not in pr_numbers:
        raise ValueError(f"PR number {pr_number} not found in board")
    pr = prs[pr_numbers.index(pr_number)]
    system_prompt = f"""
    You are a helpful assistant that reviews a GitHub pull request and generates a list of relevant labels based on the content of the pull request.
    Please provide your response in the following format:
    <label_1>, <label_2>, ...
    Say "N/A" if there are no relevant labels. Please only return existing labels that are relevant to the pull request, do not make up new labels.
    You have access to the following tools:
    """
    for tool in get_tools():
        system_prompt += f"- {tool.__name__}\n"
    
    user_input = f"Review pull request {pr.number} and generate a list of relevant labels"
    response = await query_agent(get_tools(), system_prompt, user_input)
    return response

if __name__ == "__main__":
    response = asyncio.run(review_pr_and_get_labels(66))
    print(response)
