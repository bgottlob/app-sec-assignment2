from flask import session
import re

def assertTextOut(input_text, html):
    match = re.search('<p id="textout">(.*)</p>', html)
    assert match
    assert (input_text in match.group(1))

def assertMisspelled(misspelled, html):
    match = re.search('<p id="misspelled">(.*)</p>', html)
    assert match
    assert (misspelled == match.group(1))

def test_check_words(client, routes):
    routes.register(client, 'testusername', 'testpassword', '6091234567')
    routes.login(client, 'testusername', 'testpassword', '6091234567')
    with client:
        res = routes.check_words(client, 'Hello foof world bar baz').data.decode('utf-8')
        assertTextOut('Hello foof world bar baz', res)
        assertMisspelled('foof, baz', res)
