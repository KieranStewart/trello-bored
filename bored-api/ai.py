import asyncio
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import FunctionAgent
from pydantic import BaseModel, Field
from bored_api import pr
from dotenv import load_dotenv
import os
from dataclasses import dataclass
from proxy_mgmt.proxy import BoardProxy
from tools import get_tools, get_ticket, get_all_tickets, get_all_labels, get_all_prs, get_categories

load_dotenv()

@dataclass
class TicketUpdate(BaseModel):
    ticket_id: int = Field(..., description="The ID of the ticket to update")
    new_status: str = Field(..., description="The new status for the ticket")
    description: str = Field(None, description="An optional description providing more context about the update")

async def query_agent(tools: list[function], system_prompt: str, user_input: str, output_cls = None):
    agent = FunctionAgent(
        llm=GoogleGenAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-pro"),
        tools=tools,
        system_prompt=system_prompt,
    )
    if output_cls:
        agent.output_cls = output_cls
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

async def review_pr_and_get_assoc_tickets(pr_number: int) -> str | None:
    prs = get_all_prs()
    pr_numbers = [pr.number for pr in prs]
    if pr_number not in pr_numbers:
        raise ValueError(f"PR number {pr_number} not found in board")
    pr = prs[pr_numbers.index(pr_number)]
    system_prompt = f"""
    You are a helpful assistant that reviews a GitHub pull request and generates a list of most closely related tickets based on the content of the pull request.
    Please provide your response in the following format:
    <ticket_id_1>, <ticket_id_2>, ...
    Say "N/A" if there are no relevant tickets. Please only return existing ticket IDs that are relevant to the pull request, do not make up new ticket IDs.
    Your most powerful tool is get_all_tickets, use it to review all tickets and find the most relevant ones to the PR. You can also use get_ticket to get more information about specific tickets if needed.
    You have access to the following tools:
    """
    for tool in get_tools():
        system_prompt += f"- {tool.__name__}\n"
    
    user_input = f"Review pull request {pr.number} and generate a list of associated ticket IDs"
    response = await query_agent(get_tools(), system_prompt, user_input)
    return response

async def review_merge_and_get_ticket_status_update(branch_name: str, pr_diff: str) -> TicketUpdate | None:
    system_prompt = f"""
    You are a helpful assistant that reviews the diff of a merged GitHub pull request and generates a new status recommendation for the associated ticket.
    You should determine the ticket id from the branch name and available tools, and then review the diff to understand what changes were made in the PR. 
    Based on the changes, you should generate a new status for the ticket (statuses are defined below)
    Please provide your response in the following format:
    <ticket_id (int)>: <ticket_status (str)>; <description (str, optional)>
    For example:
    123: In Progress; The PR added a new feature, so the ticket status should be updated to In Progress.
    You will need to use the tools: get_all_tickets and get_ticket to find the relevant ticket and understand its current status and description. 
    Then you will review the PR diff and determine how the changes in the PR should impact the ticket status.
    You may also need to use get_all_prs to find the PR associated with the branch name and get_pr to get more information about the PR if needed.
    Say "N/A" if there are no relevant updates. Please only return updates that are relevant to the changes made in the pull request, do not make up new updates.
    Diff:
    {pr_diff}
    You have access to the following tools:
    """
    for tool in get_tools():
        system_prompt += f"- {tool.__name__}\n"
    
    statuses = get_categories().options.keys()
    system_prompt += f"The possible ticket statuses are: {', '.join(statuses)}\n"
    
    user_input = f"Review the diff of a merged pull request with branch name {branch_name} and generate a status update for the associated ticket"
    response = await query_agent(get_tools(), system_prompt, user_input, output_cls=TicketUpdate)
    return response

if __name__ == "__main__":
    diff = """
    index 5668875..cbe83be 100644
    --- a/bored-api/ai.py
    +++ b/bored-api/ai.py
    @@ -1,30 +1,16 @@
    import asyncio
    from llama_index.llms.google_genai import GoogleGenAI
    from llama_index.core.agent.workflow import FunctionAgent
    +from bored_api import pr
    from dotenv import load_dotenv
    import os
    -from tools import get_tools
    +from proxy_mgmt.proxy import BoardProxy
    
    load_dotenv()
    
    -system_prompt = "
    -You are a helpful assistant that interacts with GitHub issues and sends simple responses.
    -Your job is to use the tools provided to you to get information about GitHub issues and their statuses.
    -You have access to the following tools:
    -"
    -
    -for tool in get_tools():
    -    system_prompt += f"- {tool.__name__}\n"
    -
    -async def main():
    -    agent = FunctionAgent(
    -        llm=GoogleGenAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash"),
    -        tools=get_tools(),
    -        system_prompt=system_prompt,
    -    )
    -    user_input = "What are the current open issues on GitHub?"
    -    response = await agent.run(user_input)
    -    print(response)
    +def get_tools():
    +    proxy = BoardProxy()
    +    return proxy.get_all_tools()
    
    async def query_agent(tools: list[function], system_prompt: str, user_input: str):
        agent = FunctionAgent(
    @@ -32,8 +18,30 @@ async def query_agent(tools: list[function], system_prompt: str, user_input: str
            tools=tools,
            system_prompt=system_prompt,
        )
    -    response = await agent.run(user_input)
    +    try:
    +        response = await agent.run(user_input)
    +    except Exception as e:
    +        print(f"Error querying agent: {e}")
    +        response = None
    +    return response
    +
    +async def review_pr_and_return_set_of_tickets(pr_url: str) -> str | None:
    +    system_prompt = f"
    +    You are a helpful assistant that reviews a GitHub PR and returns a list of possible issue IDs that might be related.
    +    Please provide your response in the following format:
    +    <issue_id_1>, <issue_id_2>, ...
    +    Say "None" if there are no linked open issues.
    +    You have access to the following tools:
    +    "
    +    for tool in get_tools():
    +        system_prompt += f"- {tool.__name__}\n"
    +    system_prompt += f"You can also use the following board proxy methods to get information about tickets:\n"
    +
    +    
    +    user_input = f"Review the PR at {pr_url} and return a list of issues"
    +    response = await query_agent(get_tools(), system_prompt, user_input)
        return response
    
    if __name__ == "__main__":
    -    asyncio.run(main())
    +    response = asyncio.run(review_pr_and_return_set_of_tickets("https://github.com/your-repo/your-pr"))
    +    print(response)
    diff --git a/bored-api/proxy_mgmt/proxy.py b/bored-api/proxy_mgmt/proxy.py
    index 1df8689..51c9b54 100644
    --- a/bored-api/proxy_mgmt/proxy.py
    +++ b/bored-api/proxy_mgmt/proxy.py
    @@ -31,3 +31,15 @@ def get_categories(self):
    
        def move_ticket(self, ticket_id, category):
            return self.provider.move_ticket(ticket_id, category)
    +    
    +    def get_all_tools(self):
    +        "
    +        This function returns a list of all the tools available in the board proxy.
    +        "
    +        return [
    +            self.get_ticket,
    +            self.get_tickets,
    +            self.get_all_tickets,
    +            self.get_categories,
    +            self.move_ticket
    +        ]
    diff --git a/bored-api/tools.py b/bored-api/tools.py
    deleted file mode 100644
    index 127cdef..0000000
    --- a/bored-api/tools.py
    +++ /dev/null
    @@ -1,22 +0,0 @@
    -# This file contains the toolchain used by the Gemini
    -# LlamaIndex agent.
    -
    -def get_github_issues() -> list:
    -    # Placeholder implementation
    -    return [
    -        {"id": 1, "title": "Issue 1", "status": "open"},
    -        {"id": 2, "title": "Issue 2", "status": "closed"},
    -    ]
    -
    -def get_issue_status(issue_id):
    -    # Placeholder implementation
    -    issues = get_github_issues()
    -    for issue in issues:
    -        if issue["id"] == issue_id:
    -            return issue["status"]
    -    return "Issue not found"
    -
    -def get_tools() -> list:
    -    return [
    -        get_github_issues, get_issue_status
    -    ]
    """
    response = asyncio.run(review_merge_and_get_ticket_status_update("dev-parse-pr-api", diff))
    print(response)
    print(response.parsed_output)
