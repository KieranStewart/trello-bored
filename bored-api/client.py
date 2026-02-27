from uuid import uuid4
from flask import Response, jsonify

"""
Sessions are how the server keeps track of which tasks a user has yet to confirm.
Sessions represent projects (github projects + github repo) and the users are inside, with an array of tasks.
"""
# FIXME save sessions to disk and load on next server startup
# FIXME remove sample sessions
# TODO Add project vs user seperation
# Should maybe switch tasks to be a dictionary for easier access when deleting and adding tasks
# Task dictionary would be refrenced by their refrence id
sessions = {
    "session0":{
        "user0":[
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
}

# FIXME change usage to match query
def query_client(session_id:str, user_id:str, tasks):
    if session_id in sessions.keys():
        if user_id in sessions[session_id].keys():
            sessions[session_id][user_id].extend(tasks)
            return Response("Succsessfully added tasks", 200)
        else if:
            new_user_id = generate_user(session_id=session_id, user_id=user_id).headers.get('user-id')
            sessions[session_id][user_id].extend(tasks)
            out = Response("Succsessfully generated user and added tasks", 201)
            out.headers.add("user-id", new_user_id)
            return out
    else:
        return Response("Session ID not found", 404)
    

def client_view(session_id:str, user_id:str):
    if session_id in sessions.keys():
        if user_id in sessions[session_id].keys():
            return jsonify(sessions[session_id][user_id])
        else:
            return Response("User ID not found", 404)
    else:
        return Response("Session ID not found", 404)

def generate_session(session_id:str=''):
    if session_id == '':
        session_id = uuid4()
    if session_id not in sessions.keys():
        sessions[session_id] = []
        out = Response("Session created with id:'" + str(session_id) + "'", 200)
        out.headers.add('session-id', str(session_id))
        return out
    else:
        # In future should prevent users from knowing when there is a session id conflict to prevent locating and stealing session ids (possibly use a two key system)
        # Also should probably clear empty sessions after some time
        return Response("Session id conflict", 400)

def generate_user(session_id:str, user_id:str=''):
    if not session_id or session_id == '':
        return Response("Session id must be specified", 400)
    if user_id == '':
        user_id = uuid4()
    if user_id in sessions[session_id].keys():
        return Response("User id conflicts with existing user", 400)
    sessions[session_id][user_id] = []
    out = Response("User created with id:'" + str(user_id) + "'", 200)
    out.headers.add('user-id', str(user_id))
    out.headers.add('session-id', str(session_id))
    return out