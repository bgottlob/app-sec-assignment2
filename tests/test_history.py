from flask import session
import re

# Assertions for /history page
def assertNumSubmissions(num, html):
    match = re.search('<span id="numqueries">(.*)</span>', html)
    assert match
    assert num == int(match.group(1))

def assertSubmissionID(id, html):
    match = re.search('<span id="query(\d+)">(.*)</span>', html)
    assert match
    print(match.group(1))
    assert id == int(match.group(1))
    assert id == int(match.group(2))

# Assertions for /history/<id> page
def assertUsername(username, html):
    match = re.search('<p id="username">(.*)</p>', html)
    assert match
    assert username == match.group(1)

def assertIndividualSubmissionID(id, html):
    match = re.search('<p id="queryid">(.*)</p>', html)
    assert match
    assert id == int(match.group(1))

def assertUserInput(user_input, html):
    match = re.search('<p id="querytext">(.*)</p>', html)
    assert match
    assert (user_input in match.group(1))

def assertMisspelled(misspelled, html):
    match = re.search('<p id="queryresults">(.*)</p>', html)
    assert match
    assert (misspelled == match.group(1))

def test_history(client, routes, registered_users):
    subs = [{ 'id': 1, 'text': 'Hello, wrold!', 'misspelled': 'wrold' },
            { 'id': 2, 'text': 'Hlelo, world!', 'misspelled': 'Hlelo' }]

    with client:
        # Create the test data - one submission per user
        routes.login(client,
                     registered_users[0]['username'],
                     registered_users[0]['password'],
                     registered_users[0]['mfa'])
        routes.check_words(client, subs[0]['text'])
        routes.logout(client)

        routes.login(client,
                     registered_users[1]['username'],
                     registered_users[1]['password'],
                     registered_users[1]['mfa'])
        routes.check_words(client, subs[1]['text'])
        routes.logout(client)

        # Read the data - each user should only see one submission, but
        # different submissions - each one's own
        routes.login(client,
                     registered_users[0]['username'],
                     registered_users[0]['password'],
                     registered_users[0]['mfa'])
        html = routes.history(client).data.decode('utf-8')
        assertNumSubmissions(1, html)
        assertSubmissionID(subs[0]['id'], html)
        routes.logout(client)

        routes.login(client,
                     registered_users[1]['username'],
                     registered_users[1]['password'],
                     registered_users[1]['mfa'])
        html = routes.history(client).data.decode('utf-8')
        assertNumSubmissions(1, html)
        assertSubmissionID(subs[1]['id'], html)

        html = routes.submission(client, subs[1]['id']).data.decode('utf-8')
        assertIndividualSubmissionID(subs[1]['id'], html)
        assertUserInput(subs[1]['text'], html)
        assertMisspelled(subs[1]['misspelled'], html)

        html = routes.submission(client, subs[0]['id']).data.decode('utf-8')
        try:
            assertIndividualSubmissionID(subs[0]['id'], html)
            assert False
        except:
            assert True
