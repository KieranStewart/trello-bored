from uuid import uuid4
from flask import Response, jsonify
from proxy_mgmt.proxy import BoardProxy

PROJ_BOARD = BoardProxy()

"""
Sessions are how the server keeps track of which tasks a user has yet to confirm.
Sessions represent projects (github projects + github repo) and the users are inside, with an array of tasks.
"""
# FIXME save sessions to disk and load on next server startup
# FIXME remove sample sessions
# TODO Add project vs user seperation
sessions = {
    "0":{}
}

def confirm_slide(session_id: str, user_id: str, task_id, confirm):
    if session_id not in sessions:
        return Response("Session ID not found", 404)
    if user_id not in sessions[session_id]:
        return Response("User ID not found", 404)
    for action in sessions[session_id][user_id]:
        if action["task_id"] == task_id:
            if confirm:
                take_action(action)
            sessions[session_id][user_id].remove(action)
            return Response("Task confirmed", 200)
    return Response("Task not found", 404)

def take_action(action: dict):
    if action["type"] == "Card Moved" and action.get("new_status"):
        PROJ_BOARD.move_ticket(action["task_id"], action["new_status"])
        return True
    print(str(action))
    return False

def query_client(session_id: str, user_id: str, tasks):
    if session_id not in sessions:
        return Response("Session ID not found", 404)
    if user_id not in sessions[session_id]:
        generate_user(session_id=session_id, user_id=user_id)
    sessions[session_id][user_id].extend(tasks)
    return Response("Successfully added tasks", 200)

def client_view(session_id: str, user_id: str):
    if session_id not in sessions:
        return Response("Session ID not found", 404)
    if user_id not in sessions[session_id]:
        return Response("User ID not found", 404)
    return jsonify(sessions[session_id][user_id])

def generate_session(session_id: str = ''):
    if session_id == '':
        session_id = str(uuid4())
    if session_id not in sessions:
        sessions[session_id] = {}
        out = Response("Session created with id:'" + session_id + "'", 200)
        out.headers.add('session-id', session_id)
        return out
    else:
        return Response("Session id conflict", 400)

def generate_user(session_id: str, user_id: str = ''):
    if not session_id:
        return Response("Session id must be specified", 400)
    if session_id not in sessions:
        return Response("Session ID not found", 404)
    if user_id == '':
        user_id = str(uuid4())
    if user_id in sessions[session_id]:
        return Response("User id conflicts with existing user", 400)
    sessions[session_id][user_id] = []
    out = Response("User created with id:'" + user_id + "'", 200)
    out.headers.add('user-id', user_id)
    out.headers.add('session-id', session_id)
    return out
