from proxy_mgmt.proxy import BoardProxy

proxy = BoardProxy()

def get_all_labels():
    """This function retrieves all labels from the board proxy."""
    print("Getting all labels")
    return proxy.get_all_labels()

def get_all_prs():
    """This function retrieves all pull requests from the board proxy."""
    print("Getting all pull requests")
    return proxy.get_all_prs()

def get_pr(pr_number):
    """This function retrieves a pull request from the board proxy using the provided pull request number.
    
    Args:
        pr_number (int): The number of the pull request to retrieve."""
    print(f"Getting pull request {pr_number}")
    return proxy.get_pr(pr_number)

def get_ticket(item_id):
    """This function retrieves a ticket from the board proxy using the provided item id.
    
    Args:
        item_id (int): The id of the ticket to retrieve.

    This function retrieves a ticket from the board proxy using the provided item id.
    """
    print(f"Getting ticket {item_id}")
    return proxy.get_ticket(item_id)

def get_tickets(category):
    """This function retrieves tickets from the board proxy using the provided category.

    Args:
        category (str): The category of tickets to retrieve.
    """
    print(f"Getting tickets in category {category}")
    return proxy.get_tickets(category)

def get_all_tickets():
    """This function retrieves all tickets from the board proxy."""
    print("Getting all tickets")
    return proxy.get_all_tickets()

def get_categories():
    """This function retrieves all categories from the board proxy."""
    print("Getting all categories")
    return proxy.get_categories()

def move_ticket(item_id, category):
    """This function moves a ticket to a different category.

    Args:
        item_id (int): The id of the ticket to move.
        category (str): The category to move the ticket to.
    """
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