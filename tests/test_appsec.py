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

# Tests that a client initially does not have a session token
def test_no_token(client):
    with client:
        client.get('/')
        assert (not 'username' in session)
        assert (len(session) == 0)
