from flask import Flask, Response, request
from update import secure_update

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return Response('Hello World! Updated 2', 200)
    elif request.method == 'POST':
        print("Posted:", request.form.keys())
        return Response('Pushed?!', 200)

@app.route('/review', methods=['POST'])
def review(): # TODO Write this endpoint (review)
    return Response('Default Response', 200)

@app.route('/merge', methods=['POST'])
def merge(): # TODO Write this endpoint (merge)
    return Response('Default Response', 200)

@app.route('/pr', methods=['POST'])
def pr(): # TODO Write this endpoint (pr)
    return Response('Default Response', 200)

@app.route('/branch', methods=['POST'])
def branch(): # TODO Write this endpoint (branch)
    return Response('Default Response', 200)

@app.route('/confirm', methods=['POST'])
def confirm(): # TODO Write this endpoint (confirm)
    return Response('Default Response', 200)

@app.route('/checkout')
def branch(): # TODO Write this endpoint (checkout)
    return Response('Default Response', 200)

@app.route('/admin/serverupdate')
def update():
    return secure_update(request.headers.get("admin-key"))

if __name__ == "__main__":
    app.run(port=8080)