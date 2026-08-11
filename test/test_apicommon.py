'''
test_apicommon - test contracts.apicommon
=========================================================
'''

# pypi
from flask import Flask

# homegrown
from contracts.apicommon import success_response, failure_response


def test_success_response_sets_success_true():
    app = Flask(__name__)
    with app.test_request_context():
        resp = success_response(foo='bar')
        assert resp.json == {'success': True, 'foo': 'bar'}


def test_success_response_with_no_extra_args():
    app = Flask(__name__)
    with app.test_request_context():
        resp = success_response()
        assert resp.json == {'success': True}


def test_failure_response_sets_success_false():
    app = Flask(__name__)
    with app.test_request_context():
        resp = failure_response(cause='bad input')
        assert resp.json == {'success': False, 'cause': 'bad input'}
