import os
import subprocess
from dotenv import load_dotenv

from flask import Response

def secure_update(admin_key):
    load_dotenv()
    server_admin_key = os.getenv('admin-key')
    if not server_admin_key:
        print("ERROR: Unsecured Admin Account, set admin-key in bored-api/.env")
        return Response("Unsecured Admin Account", 500)
    elif server_admin_key == admin_key:
        return update()
    else:
        print("WARNING: Failed Admin Update Attempt")
        return Response("Invalid Key", 401)

def update():
    try:
        result = subprocess.run(
                ['git', 'pull'],
                cwd='./',
                capture_output=True,
                text=True,
                check=True
            )
        if result.stdout == 'Already up to date.\n':
            return Response("Already up to date", 200)
        return Response("Repository Updated", 200)
    except subprocess.CalledProcessError as scpe:
        print("ERROR: During Pull:", scpe)
        return Response('Git Pull Error', 500)