import asyncio
import os
from flask import Flask, Response, request, jsonify
from update import secure_update
from client import client_view, query_client, generate_session, generate_user, confirm_slide, sessions # FIXME Remove sessions debugging
from dotenv import load_dotenv
from proxy_mgmt.proxy import BoardProxy
from ai import review_merge_and_get_ticket_status_update, review_pr_and_get_assoc_tickets, TicketUpdate

app = Flask(__name__)
board = BoardProxy()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return Response('<h1>Welcome to Bored API</h1>\nThis is the debug screen, if you are seeing this in production then don\'t.<br><br>\n' + str(sessions), 200)
    elif request.method == 'POST':
        return Response('Post recieved at default endpoint, no action taken', 200)

@app.route('/review', methods=['POST'])
def review(): # TODO Write this endpoint (review)
    return Response('Default Response', 200)

@app.route('/merge', methods=['POST'])
def merge():
    if not request.is_json:
        return Response("NOT JSON?!?!", 400)
    json_data = request.get_json()
    if not all(_ in json_data for _ in ["username", "diff", "branch-name"]):
        return Response("Things are missing", 400)

    session_id = request.headers.get("session-id")
    user_id = json_data["username"]
    ticket_update = asyncio.run(review_merge_and_get_ticket_status_update(json_data["branch-name"], json_data["diff"]))
    if ticket_update is None:
        return Response("AI could not determine ticket update", 200)

    task = {
        "type": "Card Moved",
        "description": f"Move ticket {ticket_update.ticket_id} to '{ticket_update.new_status}': {ticket_update.description}",
        "task_id": str(ticket_update.ticket_id),
        "new_status": ticket_update.new_status
    }
    return query_client(session_id, user_id, [task])

@app.route('/pr', methods=['POST'])
def pr():
    if not request.is_json:
        return Response("NOT JSON?!?!", 400)
    json_data = request.get_json()
    if not all(_ in json_data for _ in ["username", "pr-number"]):
        return Response("Things are missing", 400)

    session_id = request.headers.get("session-id")
    user_id = json_data["username"]
    pr_number = int(json_data["pr-number"])
    ticket_update: TicketUpdate = asyncio.run(review_pr_and_get_assoc_tickets(pr_number))
    description = ticket_update.description
    if description is None or str(description).strip() == "N/A":
        return Response("No description found", 200)

    task = {
        "type": "PR Review",
        "description": f"PR #{pr_number} has the following update: {description}",
        "task_id": str(ticket_update.ticket_id),
        "new_status": ticket_update.new_status
    }
    return query_client(session_id, user_id, [task])

@app.route('/test/push', methods=['POST'])
def test_push():
    if not request.is_json:
        return Response("NOT JSON?!?!", 400)
    json_data = request.get_json()
    session_id = request.headers.get("session-id")
    user_id = request.headers.get("user-id")
    task = {
        "type": json_data.get("type", "Card Moved"),
        "description": json_data.get("description", "Test card"),
        "task_id": json_data.get("task_id", "test-1"),
        "new_status": json_data.get("new_status", None)
    }
    return query_client(session_id, user_id, [task])

@app.route('/branch', methods=['POST'])
def branch(): # TODO Write this endpoint (branch)
    return Response('Default Response', 200)

@app.route('/checkout')
def checkout(): # TODO Write this endpoint (checkout)
    return Response('Default Response', 200)

@app.route('/confirm', methods=['POST', 'GET'])
def confirm():
    if request.method == 'GET':
        return client_view(session_id=request.headers.get("session-id"), user_id=request.headers.get("user-id"))
    else:
        data = request.get_json()
        return confirm_slide(
            session_id=request.headers.get("session-id"),
            user_id=request.headers.get("user-id"),
            task_id=data.get("task_id"),
            confirm=data.get("confirm")
        )

@app.route('/init', methods=['POST'])
def init():
    session_id = request.headers.get('session-id', '')
    return generate_session(session_id)

@app.route('/init/user', methods=['POST'])
def init_user():
    session_id = request.headers.get('session-id', '')
    user_id = request.headers.get('user-id', '')
    return generate_user(session_id, user_id)

@app.route('/tasks', methods=['GET'])
def tasks():
    try:
        tickets = board.get_all_tickets()
        open_tickets = [t for t in tickets if str(t.state).upper() == "OPEN"]
        return jsonify({"tasks": [{"number": t.number, "title": t.title, "state": t.state} for t in open_tickets]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        tickets = board.get_all_tickets()
        closed_tickets = [t for t in tickets if str(t.state).upper() == "CLOSED"]
        return jsonify({"tasks": [{"number": t.number, "title": t.title, "state": t.state} for t in closed_tickets]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/admin/serverupdate')
# def update():
#     return secure_update(request.headers.get("admin-key"))

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
