# Application Security - Assignment 2

[![Build Status](https://travis-ci.org/bgottlob/app-sec-assignment2.svg?branch=master)](https://travis-ci.org/bgottlob/app-sec-assignment2)

This assignment implements a simple web application using [Flask](https://palletsprojects.com/p/flask/).

## Installing Dependencies

Run `pip install -r requirements.txt` to installt the `pip` dependencies locally.

## Running the Server

Simply run `flask run`.

Optionally, you can set the `SECRET_KEY` environment variable to set your own secret key used to sign session cookies.
If you do not provide this environment variable, a random byte sequence will be generated and used as the secret key.

## Running Tests

This project uses [tox](https://tox.readthedocs.io/en/latest/) to manage test environments.
Once you have tox installed, simply run `tox` to run the unit tests.
