from recovery.DataRecovery import DataRecovery
from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello World"


@app.route("/score/<text>")
def score(text):
    dataRecovery = DataRecovery()
    print(text)
    return dataRecovery.score(text)


if __name__ == '__main__':
    app.run()
