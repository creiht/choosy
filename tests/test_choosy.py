import os
import tempfile

import pytest

from choosy import create_app
from choosy.db import get_db, init_db

# Some boilerplate test fixtures to assist with testing

# read in SQL for populating test data
with open(os.path.join(os.path.dirname(__file__), 'test_data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    """Test app"""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    # Create the DB and populate with test data
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    """Auth tests"""
    return AuthActions(client)

# Auth tests
def test_not_logged_in(client):
    resp = client.get('/')
    assert resp.status_code == 302
    assert resp.headers.get("Location") == "http://localhost/auth/login"

def test_register(client):
    # Test loading register page
    resp = client.get("/auth/register")
    assert resp.status_code == 200
    # Test actual registration
    resp = client.post("/auth/register",
                       data={
                           "username": "tester",
                           "password": "testing",
                           "password2": "testing",
                       })
    assert resp.status_code == 302
    assert resp.headers.get("Location") == "http://localhost/"

def test_login(client, auth):
    # Test loading login page
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    # Test actual login
    resp = auth.login()
    assert resp.status_code == 302
    assert resp.headers.get("Location") == "http://localhost/"

def test_logout(client, auth):
    auth.login()
    resp = auth.logout()
    assert resp.status_code == 302
    assert resp.headers.get("Location") == "http://localhost/auth/login"

# TODO: Mock out the giphy calls so that we can test the rest of the app
# TODO: MOAR Tests!


