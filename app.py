from os import environ
from flask import Flask, flash, redirect, render_template, request, session, url_for

users = {}

app = Flask(__name__)
app.secret_key = environ['SECRET_KEY']

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'username' in session:
            return redirect(url_for('index'))

        return render_template('registration.html')
    else: 
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

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'username' in session:
            return redirect(url_for('index'))

        return render_template('login.html')
    else:
        username = request.values['uname']
        password = request.values['pword']
        mfa = request.values['2fa']

        incorrect = 'Incorrect username or password'
        mfa_incorrect = 'Two-factor authentication failure'

        if username in users and password == users[username]['password']:
            if mfa == users[username]['mfa']:
                session['username'] = username
                flash('Successfully logged in as %s' % username)
                return redirect(url_for('index'))
            else:
                flash(mfa_incorrect)
                return redirect(url_for('login'))
        else:
            flash(incorrect)
            return redirect(url_for('login'))

@app.route('/logout', methods = ['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/checkWords', methods = ['GET', 'POST'])
def checkWords():
    if request.method == 'GET':
        return redirect(url_for('index'))
    if 'username' in session:
        return render_template('index.html', textout = request.values['inputtext'])
    return redirect(url_for('index'))
