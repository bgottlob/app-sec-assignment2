import os
import pathlib
import subprocess

from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)

bp = Blueprint('checkwords', __name__)

@bp.route('/checkWords', methods = ['GET', 'POST'])
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
