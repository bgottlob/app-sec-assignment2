from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/register', methods = ['GET'])
def register_page():
    return render_template('registration.html')

@app.route('/register', methods = ['POST'])
def register():
    username = request.values['uname']
    password = request.values['pword']
    phone = request.values['2fa']
    return
