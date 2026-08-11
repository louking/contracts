# from http://flask-dance.readthedocs.io/en/latest/testing.html

import os
import time

import pytest
from flask import Flask

# APP_NAME is normally supplied by Docker Compose's .env; set it here so the
# contracts package (which reads it at import time) also works for local/CI pytest runs
os.environ.setdefault('APP_NAME', 'contracts')

from contracts import create_app
from contracts.dbmodel import db
from contracts.settings import Testing
# from contracts import mail

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

# deliberately NOT using create_app(): it queries the Application table (for g.loutility)
# before any table has been created, so it can only succeed once db.create_all() has already
# run -- but the app/dbapp fixtures above build the app first, then create tables after. A bare
# Flask app with just contracts' db bound is enough for model/free-function-level tests that
# don't need the full app (routing, security, mail, etc); see test_utils.py/test_trends.py.
@pytest.fixture
def bareapp():
    """Minimal Flask app with contracts' db bound, no blueprints/extensions registered."""
    bareapp = Flask('contracts')
    bareapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # loutilities.user.model.Application/User/Role share contracts' db object via the 'users' bind
    bareapp.config['SQLALCHEMY_BINDS'] = {'users': 'sqlite:///:memory:'}
    bareapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    bareapp.config['TESTING'] = True
    db.init_app(bareapp)
    yield bareapp

@pytest.fixture
def bare_dbapp(bareapp):
    """bareapp fixture with a fresh in-memory database created for the test."""
    with bareapp.app_context():
        db.drop_all()
        db.create_all()
        yield bareapp

