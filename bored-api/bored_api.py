import os
from weakref import proxy
from flask import Flask, Response, request, jsonify
from update import secure_update
from client import client_view, query_client, generate_session, sessions # FIXME Remove sessions debugging
from dotenv import load_dotenv
from proxy_mgmt.implementations.github_projects import GithubProjects
from proxy_mgmt.proxy import BoardProxy


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
def merge(): # TODO Write this endpoint (merge)
    # Parse message
    """
    Action -> Server
{username: "github username",
 diff: "difference between main and pr"
 branch-name: "name of branch"
 action-type: "merge"}
 """
    raw_body = request.get_data()
    if not request.is_json():
        return Response("NOT JSON?!?!", 400)
    json_data = request.get_json()
    if not all(_ in json_data.keys() for _ in ["username", "diff", "branch-name", "action-type"]):
        return Response("Things are missing", 400)
    # Query AI for changes
    
    # Write changes to client
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
        return client_view(session_id=request.headers.get("session-id"), user_id=request.headers.get("user-id"))
    else:
        data = request.get_json()
        confirm = data.get('confirm')
        task_id = data.get('task_id')
        # TODO write sent changes to board
        return Response('Confirmation Status Recieved', 200)

@app.route('/init', methods=['POST'])
def init():
    session_id = request.headers.get('session-id', '')
    return generate_session(session_id)

# @app.route('/admin/serverupdate')
# def update():
#     return secure_update(request.headers.get("admin-key"))

# TODO add endpoint for fetching current tasks (open tickets)
@app.route('/tasks', methods=['GET'])
def tasks():
    try:
        tickets = board.get_all_tickets()
        open_tickets = [t for t in tickets if str(t.state).upper() == "OPEN"]
        return jsonify({
            "tasks": [
                {
                    "number": t.number,
                    "title": t.title,
                    "state": t.state,
                }
                for t in open_tickets
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching tickets: {str(e)}"}), 500
    
# TODO add endpoint for fetching historical tasks (closed tickets)
@app.route('/history', methods = ['GET'])
def history():
    try:
        tickets = board.get_all_tickets()
        closed_tickets = [t for t in tickets if str(t.state).upper() == "CLOSED"]
        return jsonify({
            "tasks": [
                {
                    "number": t.number,
                    "title": t.title,
                    "state": t.state,
                }
                for t in closed_tickets
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching tickets: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")