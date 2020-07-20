import hashlib
import hmac
import os
import sys

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from . import db

bp = Blueprint('auth', __name__)

user_sessions = {}

@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if authenticated():
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('registration.html')
    else: 
        # Extract data from form
        username = request.values['uname']
        password = request.values['pword']
        mfa = request.values['2fa']

        # Create the User object
        password_hash, salt = hash_password(password)
        user = db.User(
            username = username,
            password_hash = password_hash,
            salt = salt,
            mfa = mfa
        )

        db_session = db.create_session()
        db_session.add(user)

        category = 'success'
        try:
            # Try to commit to database
            db_session.commit()
            flash(f'Success: You registered as {username}', category)
            return redirect(url_for('index'))
        except IntegrityError as e:
            if str(e.orig) == 'UNIQUE constraint failed: user.username':
                msg = f'Failure: Username {username} is taken'
            else:
                print(e, file=sys.stderr)
                msg = 'Failure: Unknown error occurred'

            flash(msg, category)
            return render_template(
                'registration.html',
                username = username, password = password, mfa = mfa
            )

@bp.route('/login', methods = ['GET', 'POST'])
def login():
    if authenticated():
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login.html')
    else:
        # Extract data from form
        username = request.values['uname']
        password = request.values['pword']
        mfa = request.values['2fa']

        incorrect = 'Incorrect username or password'
        mfa_incorrect = 'Two-factor authentication failure'
        success = False

        category = 'result'
        db_session = db.create_session()
        try:
            user = db_session.query(db.User).filter(db.User.username == username).one()
            if verify_password(password, user.password_hash, user.salt):
                if mfa == user.mfa:
                    create_user_session(username)
                    flash(f'Successfully logged in as {username}', category)
                    success = True
                else:
                    flash(mfa_incorrect, category)
            else:
                flash(incorrect, category)
            return redirect(url_for('index'))
        except NoResultFound:
            flash(incorrect, category)
        except Exception as e:
            print(e, file = sys.stderr)
            flash('Unknown error occurred', category)
        finally:
            if success:
                return redirect(url_for('index'))
            else:
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
