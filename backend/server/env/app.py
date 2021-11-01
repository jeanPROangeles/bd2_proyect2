from flask import Flask
app = Flask(__name__)


@app.route('/<name>')
def index(name):
    return 'Hello,' + name
