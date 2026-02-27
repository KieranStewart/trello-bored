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
    number: str
    state: str
    body: str
    labels: list[Label]

@dataclass
class StatusInfo:
    field_id: str
    options: dict[str, str]

    def get_option_id(self, name: str) -> str | None:
        return self.options.get(name)

    def names(self) -> list[str]:
        return list(self.options.keys())


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
    
    def get_status(self, item):
        status_info = self.get_categories()

        for field in item["fieldValues"]["nodes"]:
            if "name" in field and field["name"] in status_info.names():
                return field["name"]
        return None
    
    def get_all_labels(self):
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                labels(first: 100) {
                    nodes {
                        id
                        name
                        color
                        description
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }
            }
        }
        """
        json = self.run_query(query, {"owner": "KieranStewart", "name": "trello-bored"})
        tags = json["data"]["repository"]["labels"]["nodes"]
        return tags

    def get_ticket(self, ticket_id: str) -> Ticket:
        query = """
        query($itemId: ID!) {
            node(id: $itemId) {
                ... on ProjectV2Item {
                    id
                    fieldValues(first: 5) {
                        nodes {
                            ... on ProjectV2ItemFieldSingleSelectValue {
                                name
                            }
                        }
                    }
                    content {
                        ... on Issue {
                            id
                            number
                            title
                            body
                            state
                            labels(first: 5) {
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
            number=item["content"]["number"],
            body=item["content"]["body"],
            state=item["content"]["state"],
            labels=labels
        )
    
    def get_tickets(self, category) -> list[Ticket]:
        return [
            ticket
            for ticket in self.get_all_tickets()
            if ticket.status == category
        ]

    def get_all_tickets(self) -> list[Ticket]:
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    items(first: 50) {
                        nodes {
                            id
                            fieldValues(first: 5) {
                                nodes {
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                        name
                                    }
                                }
                            }
                            content {
                                ... on Issue {
                                    id
                                    number
                                    title
                                    body
                                    state
                                    labels(first: 5) {
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
                number=item["content"]["number"],
                body=item["content"]["body"],
                state=item["content"]["state"],
                labels=labels
            )

            tickets.append(ticket)

        return tickets

    def get_categories(self) -> StatusInfo:
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    field(name: "Status") {
                        ... on ProjectV2SingleSelectField {
                            id
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

        return StatusInfo(
            field_id=field["id"],
            options={opt["name"]: opt["id"] for opt in field["options"]}
        )

    def move_ticket(self, ticket_id, category):
        if self.get_ticket(ticket_id).status == category:
            return

        status_info = self.get_categories()
        option_id = status_info.get_option_id(category)

        mutation = """
        mutation(
            $projectId: ID!,
            $itemId: ID!,
            $fieldId: ID!,
            $optionId: String!
        ) {
            updateProjectV2ItemFieldValue(
                input: {
                    projectId: $projectId,
                    itemId: $itemId,
                    fieldId: $fieldId,
                    value: { singleSelectOptionId: $optionId }
                }
            ) {
                projectV2Item { id }
            }
        }
        """

        variables = {
            "projectId": self.project_id,
            "itemId": ticket_id,
            "fieldId": status_info.field_id,
            "optionId": option_id
        }

        self.run_query(mutation, variables)
