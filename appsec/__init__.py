import os

from flask import (
    Flask, flash, redirect, render_template, request, session, url_for
)
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

csrf = CSRFProtect()
db = SQLAlchemy()

def create_app(secret_key, admin_password, admin_mfa, clean_db=False):
    app = Flask(__name__, instance_relative_config=True)
    from . import model
    app.config.update(
        SECRET_KEY = secret_key,
        # Uncomment the line below when using HTTPS
        #SESSION_COOKIE_SECURE = True,
        SESSION_COOKIE_HTTPONLY = True,
        SESSION_COOKIE_SAMESITE = 'Strict',
        PERMANENT_SESSION_LIFETIME = 900, # 15 minutes of inactivity
        SESSION_REFRESH_EACH_REQUEST = True,
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{model.db_file_path()}',
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    from . import db

    app.app_context().push()

    with app.app_context():
        csrf.init_app(app)
        db.init_app(app)


    # Database Setup
    if clean_db:
        db.drop_all()
    db.create_all()
    from . import auth
    auth.create_admin_account(admin_password, admin_mfa)

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
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.route('/', methods = ['GET'])
    def index():
        user = auth.authenticated()
        if user:
            return render_template('index.html',
                                   authenticated = True,
                                   is_admin = auth.is_admin(user))
        else:
            return render_template('index.html',
                                   authenticated = False,
                                   is_admin = False)

    app.register_blueprint(auth.bp)
    # Use authentication check function in jinja templates
    app.jinja_env.globals['authenticated'] = auth.authenticated

    from . import checkwords
    app.register_blueprint(checkwords.bp)

    from . import history
    app.register_blueprint(history.bp)

    return app
