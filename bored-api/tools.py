from proxy_mgmt.proxy import BoardProxy

proxy = BoardProxy()

def get_ticket(item_id):
    """
    This function retrieves a ticket from the board proxy using the provided item id.
    """
    return proxy.get_ticket(item_id)

def get_tickets(category):
    return proxy.get_tickets(category)

def get_all_tickets():
    return proxy.get_all_tickets()

def get_categories():
    return proxy.get_categories()

def move_ticket(item_id, category):
    return proxy.move_ticket(item_id, category)

def get_tools():
    return [
        get_ticket,
        get_tickets,
        get_all_tickets,
        get_categories,
        move_ticket
    ]