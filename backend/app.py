from recovery.DataRecovery import DataRecovery
from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def state():
    return dataRecovery.ini()


@app.route("/load")
def load():
    print('load')
    return dataRecovery.load()


@app.route("/score/<text>")
def score(text):
    print(text)
    return dataRecovery.score(text)


@app.route("/retrieve/<number>")
def retrieve(number):
    print(number)
    #return dataRecovery.retrieve_k_tweets(number)
    return render_template("retrieve.html", number=number)


if __name__ == '__main__':
    dataRecovery = DataRecovery()
    app.run()
