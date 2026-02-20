from uuid import uuid4
from flask import Response, jsonify

"""
Docstring for bored-api.client

"""
# FIXME save sessions to disk and load on next server startup
# FIXME remove sample sessions
sessions = {
    "0":[
        {
            "type":"Card Created",
            "description":"New card 'implement login feature' added to the to-do list",
            "timestamp":"2024-01-15 10:30 AM",
            "task_id":"1"
        },
        {
            "type": "Card Moved",
            "description": "Card 'Fix bug #123' moved from 'In Progress' to 'Done'",
            "timestamp": "2024-01-15 11:45 AM",
            "task_id":"2"
        }
    ]
}

def query_client(session_id:str, tasks):
    if session_id in sessions.keys():
        sessions[session_id].extend(tasks)
        return Response("Succsessfully added tasks", 200)
    else:
        return Response("Session ID not found", 404)
    

def client_view(session_id:str):
    if session_id in sessions.keys():
        print("1")
        return jsonify(sessions[session_id])
    else:
        return Response("Session ID not found", 404)

def generate_session(session_id:str):
    if session_id == '':
        session_id = uuid4()
    if session_id not in sessions.keys():
        sessions[session_id] = []
        out = Response("Session created with id:'" + str(session_id) + "'", 200)
        out.headers.add('session-id', str(session_id))
        return out
    else:
        # In future should prevent users from knowing when there is a session id conflict to prevent stealing session ids (possibly use a two key system)
        return Response("Session id conflict", 400)