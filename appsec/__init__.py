import os
import pathlib
import subprocess

from flask import Flask, flash, redirect, render_template, request, session, url_for

def create_app(secret_key=None):
    app = Flask(__name__, instance_relative_config=True)
    if secret_key:
        app.secret_key = secret_key
    else:
        app.secret_key = os.environ['SECRET_KEY']

    users = {}

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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
                flash('Failure: Username ' + username + ' is taken')
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
            input_text = request.values['inputtext']
            inputdir = os.path.join(os.path.dirname(__file__), 'userinput')
            pathlib.Path(inputdir).mkdir(exist_ok=True)
            wordlist = os.path.join(os.path.dirname(__file__), 'spell', 'wordlist.txt')
            filename = os.path.join(inputdir, session['username'] + '.txt')
            exe = os.path.join(os.path.dirname(__file__), 'spell', 'a.out')

            with open(filename, 'w') as f:
                f.write(request.values['inputtext'])

            cmd = exe + ' ' + filename + ' ' + wordlist

            res = subprocess.check_output([cmd], shell=True).decode('utf-8')
            
            return render_template('index.html', textout = input_text, misspelled = res.rstrip().replace('\n', ', '))
        return redirect(url_for('index'))

    return app
