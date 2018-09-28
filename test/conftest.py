# from http://flask-dance.readthedocs.io/en/latest/testing.html

import time

import pytest

from racesupportcontracts import create_app
from racesupportcontracts.dbmodel import db
from racesupportcontracts.settings import Testing
# from racesupportcontracts import mail

fake_time = time.time()

@pytest.fixture
def app():
    """Returns an app fixture with the testing configuration."""
    # app = myapp
    # app.config['TESTING'] = True
    # app.config['WTF_CSRF_ENABLED'] = False
    # app.config['DEBUG'] = False
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    app = create_app(Testing)

    # Disable sending emails during unit testing
    # mail.init_app(app)
    # assert app.debug == False
    
    # # establish app context
    # ctx = app.app_context()
    # ctx.push()
    # request.addfinalizer(ctx.pop)

    yield app


# @pytest.fixture
# def loggedin_app(app):
#     """Creates a logged-in test client instance."""
#     with app.test_client() as client:
#         with client.session_transaction() as sess:
#             sess['google_oauth_token'] = {
#                 'access_token': 'this is totally fake',
#                 'id_token': 'this is not a real token',
#                 'token_type': 'Bearer',
#                 'expires_in': '3600',
#                 'expires_at': fake_time + 3600,
#             }
#         yield client

@pytest.fixture
def loggedin_app(app):
    """Creates a logged-in test client instance."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['google_oauth_token'] = {
                'access_token': 'this is totally fake',
                'id_token': 'this is not a real token',
                'token_type': 'Bearer',
                'expires_in': '3600',
                'expires_at': fake_time + 3600,
            }
        yield client

# executed prior to each test
@pytest.fixture
def dbapp(app):
    db.drop_all()
    db.create_all()

    # Disable sending emails during unit testing
    # mail.init_app(app)
    assert app.debug == False

    yield app

# adapted from http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def client(app):
    client = app.test_client()

    yield client

