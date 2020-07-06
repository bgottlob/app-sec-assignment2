from flask import session

# Tests that a client initially does not have a session token
def test_no_token(client):
    with client:
        client.get('/')
        assert (not 'username' in session)
        assert (len(session) == 0)
