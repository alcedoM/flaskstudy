from flask import Flask, url_for
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Welcome to my friend'

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name
