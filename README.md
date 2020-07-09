# Application Security - Assignment 2

[![Build Status](https://travis-ci.org/bgottlob/app-sec-assignment2.svg?branch=master)](https://travis-ci.org/bgottlob/app-sec-assignment2)

This assignment implements a simple web application using [Flask](https://palletsprojects.com/p/flask/).

## Running the Server

Simply run `flask run`.

Optionally, you can set the `SECRET_KEY` environment variable to set your own secret key used to sign session cookies.
If you do not provide this environment variable, a random byte sequence will be generated and used as the secret key.
