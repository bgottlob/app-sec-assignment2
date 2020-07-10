import os
import pathlib
import shutil
import subprocess
import uuid

from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)

from appsec.auth import authenticated

bp = Blueprint('checkwords', __name__)

currdir = os.path.dirname(__file__)
inputdir = os.path.join(currdir, 'userinput')

# Clear the contents of the user input directory if it exists, then recreate it
# to hold user input files
if os.path.exists(inputdir):
    shutil.rmtree(inputdir)
pathlib.Path(inputdir).mkdir(exist_ok=True)

@bp.route('/spell_check', methods = ['GET', 'POST'])
def checkWords():
    if request.method == 'GET':
        return redirect(url_for('index'))
    if authenticated():
        input_text = request.values['inputtext']

        wordlist = os.path.join(currdir, 'spell', 'wordlist.txt')
        filepath = os.path.join(inputdir, f'{uuid.uuid4()}.txt')
        exe = os.path.join(currdir, 'spell', 'a.out')

        with open(filepath, 'w') as f:
            f.write(request.values['inputtext'])

        cmd = f'{exe} {filepath} {wordlist}'
        res = subprocess.check_output([cmd], shell=True).decode('utf-8')

        # Delete user input file after misspelled words are found, it is no longer needed
        #os.remove(filepath)
        
        return render_template('index.html', textout = input_text, misspelled = res.rstrip().replace('\n', ', '))

    # Redirect users who are not logged in to the home page
    return redirect(url_for('index'))
