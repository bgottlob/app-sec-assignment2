import os
import tempfile
from flask import session
import pytest
import re

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

# Verifies an appropriate success message appears in rendered HTML
def assertRegisterMessage(success, html):
    match = re.search('<li id="result">(.*)</li>', html)
    assert match
    msg = match.group(1).lower()
    if success:
        assert 'success' in msg
    else:
        assert 'failure' in msg


# Tests that a client initially does not have a session token
def test_no_token(client):
    with client:
        client.get('/')
        assert (not 'username' in session)
        assert (len(session) == 0)

def test_register(client):
    res = register(
            client,
            'testusername',
            'testpassword',
            '6091234567'
            ).data.decode('utf-8')
    assertRegisterMessage(True, res)
    res = register(
            client,
            'testusername',
            'othertestpassword',
            '6091112222'
            ).data.decode('utf-8')
    assertRegisterMessage(False, res)
