from types import FunctionType
from proxy_mgmt.proxy import BoardProxy

# This file contains the toolchain used by the Gemini
# LlamaIndex agent.

def get_github_issues() -> list:
    # TODO Implement this function to fetch open issues from GitHub and return them as a list of dictionaries
    print("Called get_github_issues")
    return [
        {"id": 1, "title": "Global Warming", "status": "open"},
        {"id": 2, "title": "LLC Formation", "status": "open"},
    ]

def get_issue_status(issue_id):
    # TODO Implement this function to fetch the status of a specific issue from GitHub using the issue_id
    print("Called get_issue_status with ID:", issue_id)
    issues = get_github_issues()
    for issue in issues:
        if issue["id"] == issue_id:
            return issue["status"]
    return "Issue not found"

def get_pr_details(pr_url):
    # TODO Implement this function to fetch PR details from GitHub using the pr_url
    print("Called get_pr_details with URL:", pr_url)
    return {
        "url": pr_url,
        "title": "Sample PR",
        "status": "open",
        "details": "Implementation of LLC formation feature."
    }

def get_tools() -> list:
    funcs = [
        obj for name, obj in globals().items()
        if isinstance(obj, FunctionType)
        and obj.__module__ == __name__
        and name != "get_tools"
    ]
    proxy = BoardProxy()
    funcs += proxy.get_all_tools()
    return funcs
