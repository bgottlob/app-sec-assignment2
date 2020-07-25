import re

# Assertions for /history page
def assertNumSubmissions(num, html):
    match = re.search('<span id="numqueries">(.*)</span>', html)
    assert match
    assert num == int(match.group(1))

def assertSubmissionID(id, html):
    match = re.search('<span id="query([0-9]+)">(.*)</span>', html)
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

def assertSubmissionNotShown(submission_id, html):
    try:
        assertIndividualSubmissionID(s['id'], html)
        assert False
    except:
        assert True

def test_history(user_clients, admin_client, routes):
    subs = [{ 'id': 1, 'text': 'Hello, wrold!', 'misspelled': 'wrold' },
            { 'id': 2, 'text': 'Hlelo, world!', 'misspelled': 'Hlelo' }]

    # Create the test data - one submission per user
    with user_clients[0] as client: routes.check_words(client, subs[0]['text'])
    with user_clients[1] as client: routes.check_words(client, subs[1]['text'])

    # Read the data - each user should only see one submission, but
    # different submissions - each one's own
    with user_clients[0] as client:
        html = routes.history(client).data.decode('utf-8')
        assertNumSubmissions(1, html)
        assertSubmissionID(subs[0]['id'], html)

        # Should NOT see the other user's submission
        html = routes.submission(client, subs[1]['id']).data.decode('utf-8')
        assertSubmissionNotShown(subs[1]['id'], html)

    with user_clients[1] as client:
        html = routes.history(client).data.decode('utf-8')
        assertNumSubmissions(1, html)
        assertSubmissionID(subs[1]['id'], html)

        html = routes.submission(client, subs[1]['id']).data.decode('utf-8')
        assertIndividualSubmissionID(subs[1]['id'], html)
        assertUserInput(subs[1]['text'], html)
        assertMisspelled(subs[1]['misspelled'], html)

        html = routes.submission(client, subs[0]['id']).data.decode('utf-8')
        assertSubmissionNotShown(subs[0]['id'], html)

    # Admin can see all submissions
    with admin_client as client:
        for s in subs:
            html = routes.submission(client, s['id']).data.decode('utf-8')
            assertIndividualSubmissionID(s['id'], html)
            assertUserInput(s['text'], html)
            assertMisspelled(s['misspelled'], html)

# Admin can filter by username
def test_history_user_search(user_clients, admin_client, registered_users, routes):
    subs = [{ 'id': 1, 'text': 'Hello, wrold!', 'misspelled': 'wrold' },
            { 'id': 2, 'text': 'Hlelo, world!', 'misspelled': 'Hlelo' }]

    # Create the test data - one submission per user
    with user_clients[0] as client: routes.check_words(client, subs[0]['text'])
    with user_clients[1] as client: routes.check_words(client, subs[1]['text'])

    with admin_client as client:
        html = routes.history_user_search(
            client,
            registered_users[0]['username']
        ).data.decode('utf-8')
        assertSubmissionID(subs[0]['id'], html)
        assertSubmissionNotShown(subs[1]['id'], html)

        html = routes.history_user_search(
            client,
            registered_users[1]['username']
        ).data.decode('utf-8')
        assertSubmissionID(subs[1]['id'], html)
        assertSubmissionNotShown(subs[0]['id'], html)

def test_history_admin_only(user_clients, registered_users, routes):
    subs = [{ 'id': 1, 'text': 'Hello, wrold!', 'misspelled': 'wrold' },
            { 'id': 2, 'text': 'Hlelo, world!', 'misspelled': 'Hlelo' }]

    # Create the test data - one submission per user
    with user_clients[0] as client: routes.check_words(client, subs[0]['text'])
    with user_clients[1] as client: routes.check_words(client, subs[1]['text'])

    # Users perform unauthorized access and are redirected back to their
    # own history pages
    with user_clients[0] as client:
        html = routes.history_user_search(client, registered_users[1]['username']).data.decode('utf-8')
        assertSubmissionNotShown(subs[1]['id'], html)

    with user_clients[1] as client:
        html = routes.history_user_search(client, registered_users[0]['username']).data.decode('utf-8')
        assertSubmissionNotShown(subs[0]['id'], html)
