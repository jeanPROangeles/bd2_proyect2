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
    nresults = dataRecovery.score(text)
    palabra = text
    print(nresults)
    #jsonify({'succes': dataRecovery.score(text)}),
    return  redirect(url_for('retrieve', number = n, query = palabra))


@app.route("/retrieve/page<number>/query=<query>", methods = ['GET'])
def retrieve(number, query):
    print(number)
    #return dataRecovery.retrieve_k_tweets(number)
    data = dataRecovery.retrieve_k_tweets(number)
    palabra = query
    page = number
    print(data)
    if(not data):
        return redirect(url_for('retrieve', number = 1, query = palabra))
    return render_template('retrieve.html', obj = data, word = palabra, Npage = page)



if __name__ == '__main__':
    dataRecovery = DataRecovery()
    app.run(debug = True, port = 5050)
