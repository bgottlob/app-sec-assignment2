# Application Security - Assignment 2

[![Build Status](https://travis-ci.org/bgottlob/app-sec-assignment2.svg?branch=master)](https://travis-ci.org/bgottlob/app-sec-assignment2)

This assignment implements a simple web application using [Flask](https://palletsprojects.com/p/flask/).

## Running the Server
`env SECRET_KEY=$(python -c 'import os; print(os.urandom(16))') FLASK_APP=appsec flask run`
