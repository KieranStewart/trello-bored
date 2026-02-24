import os
from flask import Flask, Response, request
from update import secure_update
from client import client_view, query_client, generate_session
from dotenv import load_dotenv
from proxy_mgmt.implementations.github_projects import GithubProjects

app = Flask(__name__)

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
        return client_view(session_id=request.headers.get("session-id"), user_id=request.headers.get("user-id"))
    else:
        # TODO write sent changes to board
        return Response("Not created", 400)

@app.route('/init', methods=['POST'])
def init():
    session_id = request.headers.get('session-id', '')
    return generate_session(session_id)

@app.route('/admin/serverupdate')
def update():
    return secure_update(request.headers.get("admin-key"))


if __name__ == "__main__":
    app.run(port=8080)