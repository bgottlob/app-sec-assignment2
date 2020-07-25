from flask import session
import re

def test_login_history_admin_only(user_clients, registered_users, routes):
    for client in user_clients:
        html = routes.login_history(client, registered_users[0]['username']).data.decode('utf-8')
        assert '<h1>Home</h1>' in html
        assert not '<h1>Login Session Log</h1>' in html

def test_login_history_user_search(admin_client, registered_users, user_clients, routes):
    # Admin has logged in once
    with admin_client as client:
        html = routes.login_history(client, 'admin').data.decode('utf-8')
        assert len(re.findall('<span id="login[a-f0-9-]{36}_time">', html)) == 1
