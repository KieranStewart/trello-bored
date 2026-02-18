import os
from proxy_mgmt.implementations.github_projects import GithubProjects

PROJECT_PROVIDER = "github" # change this value to update which board provider to use

class BoardProxy:
    def __init__(self):
        if PROJECT_PROVIDER == "github":
            token = os.getenv("GITHUB_TOKEN")
            project_id = os.getenv("GITHUB_PROJECT_ID")

            if not token or not project_id:
                raise ValueError("Missing GitHub token or project ID")

            self.provider = GithubProjects(token, project_id)
        else:
            raise ValueError("Unsupported board provider")

    def get_ticket(self, ticket_id):
        return self.provider.get_ticket(ticket_id)
    
    def get_tickets(self, category):
        return self.provider.get_tickets(category)

    def get_all_tickets(self):
        return self.provider.get_all_tickets()
    
    def get_categories(self):
        return self.provider.get_categories()

    def move_ticket(self, ticket_id, category):
        return self.provider.move_ticket(ticket_id, category)
