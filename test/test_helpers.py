###########################################################################################
# test_helpers - test contracts.helpers
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/31/26        Lou King        Create, covering make_runsignup_client()
#
#   Copyright 2026 Lou King.  All rights reserved
###########################################################################################

# pypi
import pytest
from flask import Flask

# homegrown
from contracts.helpers import make_runsignup_client
from contracts.runsignup import RunSignUp


@pytest.fixture
def app():
    '''minimal Flask app carrying just the RunSignUp config keys'''
    app = Flask(__name__)
    app.config['RSU_KEY'] = 'testkey'
    app.config['RSU_SECRET'] = 'testsecret'
    app.config['RSU_API_REG_TOKEN'] = 'testtoken'
    app.config['RSU_API_REG_SECRET'] = 'testregsecret'
    return app


def test_make_runsignup_client_reads_config(app):
    with app.app_context():
        client = make_runsignup_client()

    assert isinstance(client, RunSignUp)
    assert client.key == 'testkey'
    assert client.secret == 'testsecret'
    assert client.api_reg_token == 'testtoken'
    assert client.api_reg_secret == 'testregsecret'


def test_make_runsignup_client_passes_through_kwargs(app):
    with app.app_context():
        client = make_runsignup_client(debug=True)

    assert client.debug is True


def test_make_runsignup_client_missing_config_raises(app):
    del app.config['RSU_KEY']
    with app.app_context():
        with pytest.raises(KeyError):
            make_runsignup_client()
