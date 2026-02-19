<<<<<<< Updated upstream
from proxy_mgmt.interface import BoardProxyInterface

class GithubProjects(BoardProxyInterface):
    def get_ticket(self, ticket_id):
        return
    
    def get_tickets(self, category):
        return

    def get_all_tickets(self):
        return

    def get_categories(self):
        return
=======
import requests
from proxy_mgmt.interface import BoardProxyInterface
from dataclasses import dataclass

@dataclass
class Label:
    id: str
    name: str
    color: str
    description: str

@dataclass
class Ticket:
    item_id: str
    title: str
    issue_id: str
    state: str
    body: str
    labels: list[Label]


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

    def get_ticket(self, ticket_id: str) -> Ticket:
        query = """
        query($itemId: ID!) {
            node(id: $itemId) {
                ... on ProjectV2Item {
                    id
                    content {
                        ... on Issue {
                            id
                            title
                            body
                            state
                            labels(first: 100) {
                                nodes {
                                    id
                                    name
                                    color
                                    description
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        json = self.run_query(query, {"itemId": ticket_id})
        item = json["data"]["node"]

        labels: list[Label] = [
            Label(
                id=label["id"],
                name=label["name"],
                color=label.get("color"),
                description=label.get("description"),
            )
            for label in item["content"]["labels"]["nodes"]
        ]

        return Ticket(
            item_id=item["id"],
            title=item["content"]["title"],
            issue_id=item["content"]["id"],
            body=item["content"]["body"],
            state=item["content"]["state"],
            labels=labels
        )
    
    def get_tickets(self, category) -> list[Ticket]:
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
                                    body
                                    state
                                    labels(first: 100) {
                                        nodes {
                                            id
                                            name
                                            color
                                            description
                                        }
                                    }
                                }
                            }
                                fieldValues(first: 20) {
                                    nodes {
                                        ... on ProjectV2ItemFieldSingleSelectValue {
                                            name
                                        }
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
            status = None
            for field in item["fieldValues"]["nodes"]:
                if "name" not in field:
                    continue
                if field["name"] == category:
                    status = field["name"]
                    break

            if status != category:
                continue

            labels: list[Label] = [
                Label(
                    id=label["id"],
                    name=label["name"],
                    color=label.get("color"),
                    description=label.get("description"),
                )
                for label in item["content"]["labels"]["nodes"]
            ]

            tickets.append(Ticket(
                item_id=item["id"],
                title=item["content"]["title"],
                issue_id=item["content"]["id"],
                body=item["content"]["body"],
                state=item["content"]["state"],
                labels=labels
            ))

        return tickets

    def get_all_tickets(self) -> list[Ticket]:
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
                                    body
                                    state
                                    labels(first: 100) {
                                        nodes {
                                            id
                                            name
                                            color
                                            description
                                        }
                                    }
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
            labels: list[Label] = [
                Label(
                    id=label["id"],
                    name=label["name"],
                    color=label.get("color"),
                    description=label.get("description"),
                )
                for label in item["content"]["labels"]["nodes"]
            ]
            
            ticket = Ticket(
                item_id=item["id"],
                title=item["content"]["title"],
                issue_id=item["content"]["id"],
                body=item["content"]["body"],
                state=item["content"]["state"],
                labels=labels
            )

            tickets.append(ticket)

        return tickets

    def get_categories(self) -> list[str]:
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    field(name: "Status") {
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                            options {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
        """

        json = self.run_query(query, {"projectId": self.project_id})
        field = json["data"]["node"]["field"]
        return [option["name"] for option in field["options"]]
>>>>>>> Stashed changes

    def move_ticket(self, ticket_id, category):
        return
    