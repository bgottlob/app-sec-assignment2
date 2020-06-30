from os import environ
from flask import Flask, flash, redirect, render_template, request, url_for

users = {}

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
    mfa = request.values['2fa']
    new_user = { 'password': password, 'mfa': mfa }
    if username in users:
        flash('ERROR: Username ' + username + ' is taken')
        return render_template(
                'registration.html',
                username = username, password = password, mfa = mfa
               )
    else:
        flash('Success: You registered as ' + username)
        users[username] = new_user
        return redirect(url_for('index'))
