import hashlib
import hmac
import os
import sys
import uuid

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
                    create_user_session(db_session, user)
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
    success = False
    try:
        if ('id' in session) and ('username' in session):
            db_session = db.create_session()
            auth_session = db_session.query(db.AuthSession).filter(
                db.AuthSession.id == session['id']
            ).join(db.User).filter(
                db.User.username == session['username']
            ).one()

            print(auth_session)

            # If this statement is reached, there is a session for this user
            success = True
    except Exception as e:
        print(e, file = sys.stderr)
    finally:
        return success

def create_user_session(db_session, user):
    # Clear previous auth session(s) to prevent session fixation
    invalidate_user_session(db_session, user)

    auth_sess_id = str(uuid.uuid4())
    # Create new server-side auth session
    auth_sess = db.AuthSession(id = auth_sess_id, user_id = user.id)

    db_session.add(auth_sess)
    db_session.commit()

    # Create the client-side session
    session.permanent = True
    session['username'] = user.username
    session['id'] = auth_sess_id

def invalidate_user_session(db_session, user):
    # Clear the server-side session(s)
    auth_sessions = db_session.query(db.AuthSession).filter(db.AuthSession.user_id == user.id).all()
    for auth_sess in auth_sessions:
        db_session.delete(auth_sess)

    # Clear the client-side session
    if session:
        session.clear()
