from proxy_mgmt.interface import BoardProxyInterface

class GithubProjects(BoardProxyInterface):
    def get_ticket(self, ticket_id):
        return {
            "id": ticket_id,
            "title": "Example Ticket",
            "status": "In Progress",
            "assignee": "First Last"
        }
    
    def get_tickets(self, category):
        return []

    def get_all_tickets(self):
        return []

    def get_categories(self):
        return []

    def move_ticket(self, ticket_id, category):
        return
    