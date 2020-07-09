import hashlib
import hmac
import os

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

bp = Blueprint('auth', __name__)

users = {}

@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if 'username' in session:
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
    if 'username' in session:
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
                session.permanent = True
                session['username'] = username
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
