import os
import tempfile
from flask import session
import pytest

import appsec

@pytest.fixture
def app():
    app = appsec.create_app(os.urandom(16))
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Helpers
def register(client, username, password, mfa):
    return client.post('/register', data = {
        'uname': username,
        'pword': password,
        '2fa': mfa
    }, follow_redirects = True)

def register_message(success, username):
    return 

# Tests that a client initially does not have a session token
def test_no_token(client):
    with client:
        client.get('/')
        assert (not 'username' in session)
        assert (len(session) == 0)


def test_register_and_login(client):
    rv = register(client, 'testusername', 'testpassword', '6091234567').data.decode('utf-8')
    assert 'Success' in rv


#def test_incorrect_login():
#
#def test_incorrect_mfa():
