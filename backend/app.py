from types import MethodDescriptorType
from recovery.DataRecovery import DataRecovery
from flask import (
Flask, 
render_template, 
request, 
redirect, 
url_for, 
jsonify
)
app = Flask(__name__, template_folder= '../frontend/', static_folder = '../frontend/')


@app.route("/")
def state():
    dataRecovery.ini()
    return  render_template('index.html')


@app.route("/load", methods = ['GET'])
def load():
    print('load')
    dataRecovery.load()
    return url_for('index')


@app.route("/score/<text>", methods = ['POST'])
def score(text):
    print(text)
    n = 1
    dataRecovery.score(text)
    #jsonify({'succes': dataRecovery.score(text)}),
    return  redirect(url_for('retrieve', number = n))


@app.route("/retrieve/<number>", methods = ['GET'])
def retrieve(number):
    print(number)
    #return dataRecovery.retrieve_k_tweets(number)
    #print(data)
    return render_template('retrieve.html', obj = dataRecovery.retrieve_k_tweets(number))



if __name__ == '__main__':
    dataRecovery = DataRecovery()
    app.run(debug = True, port = 5050)
