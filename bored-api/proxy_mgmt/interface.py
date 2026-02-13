from abc import ABC, abstractmethod

class BoardProxyInterface(ABC):
    @abstractmethod
    def get_ticket(self, ticket_id):
        pass
    
    @abstractmethod
    def get_tickets(self, category):
        pass

    @abstractmethod
    def get_all_tickets(self):
        pass

    @abstractmethod
    def get_categories(self):
        pass

    @abstractmethod
    def move_ticket(self, ticket_id, category):
        pass
    