import hashlib
import hmac
import os
import sys
import uuid

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from appsec import db

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from . import model

bp = Blueprint('auth', __name__)

user_sessions = {}

def create_admin_account():
    admin = db.session.query(model.User).filter_by(username = 'admin').one_or_none()
    if admin == None:
        # Required hard-coded admin credentials
        username = 'admin'
        password = 'Administrator@1'
        mfa = '12345678901'

        # Create the admin User object
        password_hash, salt = hash_password(password)
        admin = model.User(
            username = username,
            password_hash = password_hash,
            salt = salt,
            mfa = mfa
        )
        db.session.add(admin)
        db.session.commit()

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
        user = model.User(
            username = username,
            password_hash = password_hash,
            salt = salt,
            mfa = mfa
        )

        db.session.add(user)

        category = 'success'
        try:
            # Try to commit to database
            db.session.commit()
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
        try:
            user = db.session.query(model.User).filter(model.User.username == username).one()
            if verify_password(password, user.password_hash, user.salt):
                if mfa == user.mfa:
                    create_user_session(user)
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
    user = None
    try:
        if ('id' in session) and ('username' in session):
            auth_session, user = db.session.query(
                model.AuthSession, model.User
            ).filter(
                model.AuthSession.id == session['id']
            ).join(model.User).filter(
                model.User.username == session['username']
            ).one()
    except Exception as e:
        print(e, file = sys.stderr)
    finally:
        return user

def is_admin(user):
    return user.username == 'admin'

def create_user_session(user):
    # Clear previous auth session(s) to prevent session fixation
    invalidate_user_session(user)

    auth_sess_id = str(uuid.uuid4())
    # Create new server-side auth session
    auth_sess = model.AuthSession(id = auth_sess_id, user_id = user.id)

    db.session.add(auth_sess)
    db.session.commit()

    # Create the client-side session
    session.permanent = True
    session['username'] = user.username
    session['id'] = auth_sess_id

def invalidate_user_session(user):
    # Clear the server-side session(s)
    auth_sessions = db.session.query(model.AuthSession).filter(model.AuthSession.user_id == user.id).all()
    for auth_sess in auth_sessions:
        db.session.delete(auth_sess)
    db.session.commit()

    # Clear the client-side session
    if session:
        session.clear()
