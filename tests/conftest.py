import appsec
import os
import pytest

@pytest.fixture
def app():
    app = appsec.create_app(os.urandom(16), clean_db=True)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
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

    @staticmethod
    def history(client):
        return client.get('/history', follow_redirects = True)

    @staticmethod
    def submission(client, submission_id):
        return client.get(f'/history/query{submission_id}',
                          follow_redirects = True)

@pytest.fixture
def routes():
    return Routes

# Create pre-defined user accounts
@pytest.fixture
def registered_users(client, routes):
    users = [
        { 'username': 'user_a', 'password': 'password_a', 'mfa': '1234567890' },
        { 'username': 'user_b', 'password': 'password_b', 'mfa': '1234567890' }
    ]
    with client:
        for u in users:
            routes.register(client, u['username'], u['password'], u['mfa'])
    return users

# A list of clients for non-admin users
@pytest.fixture
def user_clients(app, registered_users, routes):
    clients = []
    for u in registered_users:
        c = app.test_client()
        with c:
            routes.login(c, u['username'], u['password'], u['mfa'])
        clients.append(c)
    return clients

# A client for an admin user
@pytest.fixture
def admin_client(client, routes):
    with client:
        routes.login(client, 'admin', 'Administrator@1', '12345678901')
    return client
