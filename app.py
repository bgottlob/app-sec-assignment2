from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('registration.html')

@app.route('/register', methods = ['POST'])
def register():
    username = request.values['uname']
    password = request.values['pword']
    phone = request.values['phone']
    return
