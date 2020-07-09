import appsec
import os
import pytest

@pytest.fixture
def app():
    app = appsec.create_app(os.urandom(16))
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Route helpers
class Routes:
    @staticmethod
    def register(client, username, password, mfa):
        return client.post('/register', data = {
            'uname': username,
            'pword': password,
            '2fa': mfa
        }, follow_redirects = True)

    @staticmethod
    def login(client, username, password, mfa):
        return client.post('/login', data = {
            'uname': username,
            'pword': password,
            '2fa': mfa
        }, follow_redirects = True)

    @staticmethod
    def logout(client):
        return client.get('/logout', follow_redirects = True)

    @staticmethod
    def check_words(client, input_text):
        return client.post('/spell_check', data = {
            'inputtext': input_text
        }, follow_redirects = True)

@pytest.fixture
def routes():
    return Routes
