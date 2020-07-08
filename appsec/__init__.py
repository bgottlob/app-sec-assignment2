import os

from flask import (
    Flask, flash, redirect, render_template, request, session, url_for
)

def create_app(secret_key=None):
    app = Flask(__name__, instance_relative_config=True)
    if secret_key:
        app.secret_key = secret_key
    else:
        app.secret_key = os.environ['SECRET_KEY']

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.after_request
    def add_response_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.route('/', methods = ['GET'])
    def index():
        return render_template('index.html')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import checkwords
    app.register_blueprint(checkwords.bp)

    return app
