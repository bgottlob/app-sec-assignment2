from flask import session
import re

# Assertions for HTML elements required in project specification
# Verifies an appropriate success message appears in rendered HTML
def assertRegisterMessage(success, html):
    match = re.search('<li id="success">(.*)</li>', html)
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

# Authentication test cases
def test_register(client, routes):
    res = routes.register(
            client,
            __name__,
            'testpassword',
            '6091234567'
            ).data.decode('utf-8')
    assertRegisterMessage(True, res)
    res = routes.register(
            client,
            __name__,
            'othertestpassword',
            '6091112222'
            ).data.decode('utf-8')
    assertRegisterMessage(False, res)

def test_login_logout(client, routes):
    routes.register(client, __name__, 'testpassword', '6091234567')
    with client:
        res = routes.login(client, __name__, 'testpassword', '6091234567').data.decode('utf-8')
        assertLoginMessage('mfs', res)
        assert 'username' in session
        assert session['username'] == __name__
        routes.logout(client)
        assert (not 'username' in session)

def test_incorrect_login(client, routes):
    routes.register(client, __name__, 'testpassword', '6091234567')
    with client:
        res = routes.login(client, __name__, 'testpassword!', '6091234567').data.decode('utf-8')
        assert (not 'username' in session)
        assertLoginMessage('incorrect', res)
        res = routes.login(client, f'{__name__}!', 'testpassword', '6091234567').data.decode('utf-8')
        assert (not 'username' in session)
        assertLoginMessage('incorrect', res)

def test_mfa_failure(client, routes):
    routes.register(client, __name__, 'testpassword', '6091234567')
    with client:
        res = routes.login(client, __name__, 'testpassword', '6091111111').data.decode('utf-8')
        assert (not 'username' in session)
        assertLoginMessage('mfa', res)
