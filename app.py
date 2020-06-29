from os import environ
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = environ['SECRET_KEY']

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
    flash('You succesfully registered as ' + username)
    return redirect(url_for('index'))
