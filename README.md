# Application Security - Assignment 2

This assignment implements a simple web application using [Flask](https://palletsprojects.com/p/flask/).

## Running the Server
`env SECRET_KEY=$(python -c 'import os; print(os.urandom(16))') FLASK_APP=app.py flask run`
