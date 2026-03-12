import os
from weakref import proxy
from flask import Flask, Response, request, jsonify
from update import secure_update
from client import client_view, query_client, generate_session
from dotenv import load_dotenv
from proxy_mgmt.implementations.github_projects import GithubProjects
from proxy_mgmt.proxy import BoardProxy


app = Flask(__name__)
board = BoardProxy()
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return Response('Hello World!', 200)
    elif request.method == 'POST':
        print("Posted:", request.form.keys())
        return Response('Pushed?!', 200)

@app.route('/review', methods=['POST'])
def review(): # TODO Write this endpoint (review)
    return Response('Default Response', 200)

@app.route('/merge', methods=['POST'])
def merge(): # TODO Write this endpoint (merge)
    # Query AI for changes
    # Write changes to client
    return Response('Default Response', 200)

@app.route('/pr', methods=['POST'])
def pr(): # TODO Write this endpoint (pr)
    return Response('Default Response', 200)

@app.route('/branch', methods=['POST'])
def branch(): # TODO Write this endpoint (branch)
    return Response('Default Response', 200)

@app.route('/checkout')
def checkout(): # TODO Write this endpoint (checkout)
    return Response('Default Response', 200)

@app.route('/confirm', methods=['POST', 'GET'])
def confirm():
    if request.method == 'GET':
        print("getting")
        return client_view(request.headers.get("session-id"))
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

@app.route('/admin/serverupdate')
def update():
    return secure_update(request.headers.get("admin-key"))

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
if __name__ == "__main__":
    app.run(port=8080)