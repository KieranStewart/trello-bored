from datetime import datetime
import os
from flask import Flask, Response, request
from update import secure_update
import client
from dotenv import load_dotenv
from proxy_mgmt.implementations.github_projects import GithubProjects
import tools
from uuid import uuid4

import ai

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return Response('<h1>Welcome to Bored API</h1>\nThis is the debug screen, if you are seeing this in production then don\'t.<br><br>\n' + str(client.sessions), 200)
    elif request.method == 'POST':
        return Response('Post recieved at default endpoint, no action taken', 200)

@app.route('/review', methods=['POST'])
def review(): # TODO Write this endpoint (review)
    return Response('Default Response', 200)

@app.route('/merge', methods=['POST'])
def merge(): # TODO Write this endpoint (merge)
    # Parse message
    """
    Action -> Server
{username: "github username",
 diff: "difference between main and pr"
 branch-name: "name of branch"
 action-type: "merge"}
 """
    # Retrieve session id from header
    session_id = request.headers.get("session-id")
    # TODO Find user id
    request.headers.get("username")
    # Check request formatting
    if not request.is_json():
        return Response("NOT JSON?!?!", 400)
    json_data = request.get_json()
    if not all(_ in json_data.keys() for _ in ["username", "diff", "branch-name", "action-type"]):
        return Response("Things are missing", 400)
    # Query AI for changes
    # TODO Make AI review merge based on changes and branch name and returns json:
    """
    [
        {ticket-id:<ticket id>, target-catagory-id:<the catagory identifier>, description: "A short description"}
    ]
    """
    changes = ai.review_merge_and_get_assoc_tickets(diff=json_data["diff"], branch_name=json_data["branch-name"])
    # Write changes to client
    tasks = []
    for change in changes:
        tasks.add({
                "type": "Card Moved",
                "description": "Stand in description", # FIXME maybe we get description from ai
                "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                "task_id":uuid4(),
                "ticket-id":change["ticket-id"],
                "target-catagory-id":change["target-catagory-id"]
            })
    client.query_client(session_id, tasks=tasks)
        
    return Response('Default Response', 200)

@app.route('/pr', methods=['POST'])
def pr(): # TODO Write this endpoint (pr)raw_body = request.get_data()
    if not request.is_json():
        return Response("NOT JSON?!?!", 400)
    json_data = request.get_json()
    if not all(_ in json_data.keys() for _ in ["username", "diff", "branch-name", "action-type"]):
        return Response("Things are missing", 400)
    
    

@app.route('/branch', methods=['POST'])
def branch(): # TODO Write this endpoint (branch)
    return Response('Default Response', 200)

@app.route('/checkout')
def checkout(): # TODO Write this endpoint (checkout)
    return Response('Default Response', 200)

@app.route('/confirm', methods=['POST', 'GET'])
def confirm():
    if request.method == 'GET':
        return client.client_view(session_id=request.headers.get("session-id"), user_id=request.headers.get("user-id"))
    else:
        # TODO write sent changes to board
        return Response("Not created", 400)

@app.route('/init', methods=['POST'])
def init():
    session_id = request.headers.get('session-id', '')
    return client.generate_session(session_id)

# @app.route('/admin/serverupdate')
# def update():
#     return secure_update(request.headers.get("admin-key"))


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")