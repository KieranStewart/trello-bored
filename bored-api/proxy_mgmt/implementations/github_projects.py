import requests
from proxy_mgmt.interface import BoardProxyInterface
from dataclasses import dataclass

@dataclass
class Ticket:
    item_id: str
    title: str
    issue_id: str


class GithubProjects(BoardProxyInterface):
    def __init__(self, token, project_id):
        self.url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}"
        }
        self.project_id = project_id

    def run_query(self, query, variables=None):
        response = requests.post(
            self.url,
            json={"query": query, "variables": variables},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_ticket(self, ticket_id):
        return
    
    def get_tickets(self, category):
        return

    def get_all_tickets(self):
        query = """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      id
                      title
                    }
                  }
                }
              }
            }
          }
        }
        """

        json = self.run_query(query, {"projectId": self.project_id})
        items = json["data"]["node"]["items"]["nodes"]
        tickets: list[Ticket] = []

        for item in items:
            ticket = Ticket(
                item_id=item["id"],
                title=item["content"]["title"],
                issue_id=item["content"]["id"]
            )

            tickets.append(ticket)

        return tickets

    def get_categories(self):
        return

    def move_ticket(self, ticket_id, category):
        return
    