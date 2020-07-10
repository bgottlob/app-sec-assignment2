import hashlib
import hmac
import os

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

bp = Blueprint('auth', __name__)

users = {}
user_sessions = {}

@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if authenticated():
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('registration.html')
    else: 
        username = request.values['uname']
        password = request.values['pword']
        mfa = request.values['2fa']
        password_hash, salt = hash_password(password)
        new_user = { 'password_hash': password_hash, 'salt': salt, 'mfa': mfa }
        category = 'success'
        if username in users:
            flash('Failure: Username ' + username + ' is taken', category)
            return render_template(
                    'registration.html',
                    username = username, password = password, mfa = mfa
                   )
        else:
            flash('Success: You registered as ' + username, category)
            users[username] = new_user
            return redirect(url_for('index'))

@bp.route('/login', methods = ['GET', 'POST'])
def login():
    if authenticated():
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.values['uname']
        password = request.values['pword']
        mfa = request.values['2fa']

        category = 'result'

        incorrect = 'Incorrect username or password'
        mfa_incorrect = 'Two-factor authentication failure'

        if username in users and verify_password(password, users[username]['password_hash'], users[username]['salt']):
            if mfa == users[username]['mfa']:
                create_user_session(username)
                flash('Successfully logged in as %s' % username, category)
                return redirect(url_for('index'))
            else:
                flash(mfa_incorrect, category)
                return redirect(url_for('auth.login'))
        else:
            flash(incorrect, category)
            return redirect(url_for('auth.login'))

@bp.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    if authenticated():
        invalidate_user_session(session['username'])
    return redirect(url_for('index'))

def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, 100000)
    return password_hash, salt

def verify_password(password, password_hash, salt):
    return hmac.compare_digest(
        password_hash,
        hashlib.pbkdf2_hmac('sha512', password.encode(), salt, 100000)
    )

def authenticated():
    return ('nonce' in session) and ('username' in session) and (user_sessions[session['username']] == session['nonce'])

def create_user_session(username):
    invalidate_user_session(username)
    nonce = os.urandom(16)
    # Create the client-side session
    session.permanent = True
    session['username'] = username
    session['nonce'] = nonce
    # Track the session on the server side
    user_sessions[username] = nonce

def invalidate_user_session(username):
    # Clear the server-side session
    if username in user_sessions:
        del user_sessions[username]
    # Clear the client-side session
    if session:
        session.clear()
