from proxy_mgmt.proxy import BoardProxy

proxy = BoardProxy()

def get_all_labels():
    print("Getting all labels")
    return proxy.get_all_labels()

def get_all_prs():
    print("Getting all pull requests")
    return proxy.get_all_prs()

def get_pr(pr_number):
    print(f"Getting pull request {pr_number}")
    return proxy.get_pr(pr_number)

def get_ticket(item_id):
    """
    This function retrieves a ticket from the board proxy using the provided item id.
    """
    print(f"Getting ticket {item_id}")
    return proxy.get_ticket(item_id)

def get_tickets(category):
    print(f"Getting tickets in category {category}")
    return proxy.get_tickets(category)

def get_all_tickets():
    print("Getting all tickets")
    return proxy.get_all_tickets()

def get_categories():
    print("Getting all categories")
    return proxy.get_categories()

def move_ticket(item_id, category):
    print(f"Moving ticket {item_id} to category {category}")
    return proxy.move_ticket(item_id, category)

def get_tools():
    return [
        get_ticket,
        get_tickets,
        get_all_tickets,
        get_categories,
        move_ticket,
        get_all_labels,
        get_all_prs,
        get_pr
    ]