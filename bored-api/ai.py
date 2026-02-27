import asyncio
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import FunctionAgent
from bored_api import pr
from dotenv import load_dotenv
import os
from proxy_mgmt.proxy import BoardProxy
from tools import get_tools, get_ticket, get_all_tickets, get_all_labels

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

async def review_pr_and_return_set_of_tickets(pr_num: str) -> str | None:
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

    
    user_input = f"Review PR #{pr_num} and return a list of issues"
    response = await query_agent(get_tools(), system_prompt, user_input)
    return response

async def review_ticket_and_generate_labels(ticket_id: int) -> str | None:
    tickets = get_all_tickets()
    # print(tickets)
    ticket_ids = [ticket.number for ticket in tickets]
    if ticket_id not in ticket_ids:
        raise ValueError(f"Ticket ID {ticket_id} not found in board")
    ticket = tickets[ticket_ids.index(ticket_id)]
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

if __name__ == "__main__":
    response = asyncio.run(review_ticket_and_generate_labels(63))
    print(response)
