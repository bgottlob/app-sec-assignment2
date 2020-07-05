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

def login(client, username, password, mfa):
    return client.post('/login', data = {
        'uname': username,
        'pword': password,
        '2fa': mfa
    }, follow_redirects = True)

def logout(client):
    return client.get('/logout', follow_redirects = True)

# Verifies an appropriate success message appears in rendered HTML
def assertRegisterMessage(success, html):
    match = re.search('<li id="result">(.*)</li>', html)
    assert match
    msg = match.group(1).lower()
    if success:
        assert 'success' in msg
    else:
        assert 'failure' in msg

def assertLoginMessage(msg_type, html):
    match = re.search('<li id="result">(.*)</li>', html)
    assert match
    msg = match.group(1).lower()
    if msg_type == 'incorrect':
        assert 'incorrect' in msg
    elif msg_type == 'mfa':
        assert 'two-factor' in msg
        assert 'failure' in msg
    else:
        assert 'success' in msg

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

def test_login_logout(client):
    register(client, 'testusername', 'testpassword', '6091234567')
    with client:
        res = login(client, 'testusername', 'testpassword', '6091234567').data.decode('utf-8')
        assertLoginMessage('mfs', res)
        assert 'username' in session
        assert session['username'] == 'testusername'
        logout(client)
        assert (not 'username' in session)
        assert (len(session) == 0)

def test_incorrect_login(client):
    register(client, 'testusername', 'testpassword', '6091234567')
    with client:
        res = login(client, 'testusername', 'testpassword!', '6091234567').data.decode('utf-8')
        assert (not 'username' in session)
        assert (len(session) == 0)
        assertLoginMessage('incorrect', res)
        res = login(client, 'testusername!', 'testpassword', '6091234567').data.decode('utf-8')
        assert (not 'username' in session)
        assert (len(session) == 0)
        assertLoginMessage('incorrect', res)

def test_mfa_failure(client):
    register(client, 'testusername', 'testpassword', '6091234567')
    with client:
        res = login(client, 'testusername', 'testpassword', '6091111111').data.decode('utf-8')
        assert (not 'username' in session)
        assert (len(session) == 0)
        assertLoginMessage('mfa', res)
