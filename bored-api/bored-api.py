from flask import Flask, Response, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return Response('Hello World!', 200)
    elif request.method == 'POST':
        print("Posted:", request.form)

@app.route('/review')
def review(): # TODO Write this endpoint (review)
    return Response('Default Response', 200)

@app.route('/merge')
def merge(): # TODO Write this endpoint (merge)
    return Response('Default Response', 200)

@app.route('/pr')
def pr(): # TODO Write this endpoint (pr)
    return Response('Default Response', 200)

@app.route('/branch')
def branch(): # TODO Write this endpoint (branch)
    return Response('Default Response', 200)

if __name__ == "__main__":
    app.run(port=8080)