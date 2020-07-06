from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

bp = Blueprint('auth', __name__)

users = {}

@bp.route('/register', methods = ['GET', 'POST'])
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
            flash('Failure: Username ' + username + ' is taken')
            return render_template(
                    'registration.html',
                    username = username, password = password, mfa = mfa
                   )
        else:
            flash('Success: You registered as ' + username)
            users[username] = new_user
            return redirect(url_for('index'))

@bp.route('/login', methods = ['GET', 'POST'])
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
                return redirect(url_for('auth.login'))
        else:
            flash(incorrect)
            return redirect(url_for('auth.login'))

@bp.route('/logout', methods = ['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
