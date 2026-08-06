###########################################################################################
# test_runsignup - test contracts.runsignup.RunSignUp
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/31/26        Lou King        Create, covering the RunSignupBase refactor
#
#   Copyright 2026 Lou King.  All rights reserved
###########################################################################################

# standard
from unittest.mock import Mock

# pypi
import pytest
from flask import Flask

# homegrown
from contracts.runsignup import RunSignUp, coupons_url, race_url, raceparticipants_url, removedparticipants_url
from running.runsignup import RunSignupBase, accessError


@pytest.fixture
def app():
    '''minimal Flask app, just enough for current_app.logger.debug() calls'''
    return Flask(__name__)


@pytest.fixture
def rsu(app):
    with app.app_context():
        client = RunSignUp(key='testkey', secret='testsecret', api_reg_token='testtoken', api_reg_secret='testregsecret')
        client.open()
        yield client
        client.close()


def test_is_runsignupbase_subclass():
    '''the whole point of the refactor: shared auth/session code comes from running.runsignup.RunSignupBase'''
    assert issubclass(RunSignUp, RunSignupBase)


def test_open_sets_credentials_and_header(rsu):
    assert rsu.client_credentials == {
        'api_key': 'testkey',
        'api_secret': 'testsecret',
        'rsu_api_reg': 'testtoken',
    }
    assert rsu.session.headers.get('X-RSU-API-REG-SECRET') == 'testregsecret'


def test_close_clears_credentials(rsu):
    rsu.close()
    assert rsu.client_credentials == {}


def test_getcoupons_single_page(rsu, monkeypatch):
    calls = []
    def fake_rsuget(methodurl, **payload):
        calls.append((methodurl, payload))
        return {'coupons': [{'coupon_code': 'ABC123'}]}
    monkeypatch.setattr(rsu, '_rsuget', fake_rsuget)

    coupons = rsu.getcoupons(12345)

    assert coupons == [{'coupon_code': 'ABC123'}]
    assert len(calls) == 1
    methodurl, payload = calls[0]
    assert methodurl == coupons_url.format(race_id=12345)
    assert payload == {'page': 1, 'results_per_page': 100}


def test_getcoupons_filters_by_coupon_code(rsu, monkeypatch):
    def fake_rsuget(methodurl, **payload):
        assert payload['coupon_code'] == 'MYCODE'
        return {'coupons': []}
    monkeypatch.setattr(rsu, '_rsuget', fake_rsuget)

    coupons = rsu.getcoupons(12345, coupon_code='MYCODE')

    assert coupons == []


def test_getcoupons_paginates(rsu, monkeypatch):
    # first page full (BITESIZE=100), second page partial -> loop should fetch both then stop
    page1 = {'coupons': [{'coupon_code': f'C{i}'} for i in range(100)]}
    page2 = {'coupons': [{'coupon_code': 'CLAST'}]}
    responses = [page1, page2]
    calls = []
    def fake_rsuget(methodurl, **payload):
        calls.append(payload['page'])
        return responses.pop(0)
    monkeypatch.setattr(rsu, '_rsuget', fake_rsuget)

    coupons = rsu.getcoupons(12345)

    assert len(coupons) == 101
    assert calls == [1, 2]


def test_setcoupon_builds_request_payload(rsu, monkeypatch):
    captured = {}
    def fake_rsupost(methodurl, **params):
        captured['methodurl'] = methodurl
        captured['params'] = params
        return {'coupons': [{'coupon_id': 999}]}
    monkeypatch.setattr(rsu, '_rsupost', fake_rsupost)

    result = rsu.setcoupon(12345, 'MYCODE', '2026-01-01', '2026-12-31', 5, 'Acme Race', coupon_id=42)

    assert result == [{'coupon_id': 999}]
    assert captured['methodurl'] == coupons_url.format(race_id=12345)
    assert captured['params']['race_id'] == 12345
    assert captured['params']['request_format'] == 'json'
    from json import loads
    request = loads(captured['params']['request'])
    coupon = request['coupons'][0]
    assert coupon['coupon_id'] == 42
    assert coupon['coupon_code'] == 'MYCODE'
    assert coupon['start_date'] == '2026-01-01 00:00:00'
    assert coupon['end_date'] == '2026-12-31 23:59:59'
    assert coupon['max_num_race_registrants'] == 5
    assert coupon['coupon_notes'] == 'Acme Race'


def test_getraceevents(rsu, monkeypatch):
    def fake_rsuget(methodurl):
        assert methodurl == race_url.format(race_id=555)
        return {'race': {'events': [{'event_id': 1}, {'event_id': 2}]}}
    monkeypatch.setattr(rsu, '_rsuget', fake_rsuget)

    events = rsu.getraceevents(555)

    assert events == [{'event_id': 1}, {'event_id': 2}]


def test_getraceparticipants_single_page(rsu, monkeypatch):
    def fake_rsuget(methodurl, **payload):
        assert methodurl == raceparticipants_url.format(race_id=1)
        assert payload['event_id'] == 2
        return [{'participants': [{'user_id': 1}]}]
    monkeypatch.setattr(rsu, '_rsuget', fake_rsuget)

    participants = rsu.getraceparticipants(1, 2)

    assert participants == [{'user_id': 1}]


def test_getraceparticipants_stops_on_missing_key(rsu, monkeypatch):
    monkeypatch.setattr(rsu, '_rsuget', lambda methodurl, **payload: [{}])

    participants = rsu.getraceparticipants(1, 2)

    assert participants == []


def test_getremovedparticipants_single_page(rsu, monkeypatch):
    def fake_rsuget(methodurl, **payload):
        assert methodurl == removedparticipants_url.format(race_id=1)
        return [{'event': {'participants': [{'user_id': 9}]}}]
    monkeypatch.setattr(rsu, '_rsuget', fake_rsuget)

    removed = rsu.getremovedparticipants(1, 2)

    assert removed == [{'user_id': 9}]


def test_getremovedparticipants_stops_when_no_event_key(rsu, monkeypatch):
    monkeypatch.setattr(rsu, '_rsuget', lambda methodurl, **payload: [{}])

    removed = rsu.getremovedparticipants(1, 2)

    assert removed == []


def test_rsupost_success(rsu):
    fake_resp = Mock(status_code=200)
    fake_resp.json.return_value = {'coupons': [{'coupon_id': 1}]}
    rsu.session.post = Mock(return_value=fake_resp)

    data = rsu._rsupost('https://api.runsignup.com/rest/race/1/coupons', request='{}')

    assert data == {'coupons': [{'coupon_id': 1}]}
    _, kwargs = rsu.session.post.call_args
    assert kwargs['data']['api_key'] == 'testkey'
    assert kwargs['data']['format'] == 'json'


def test_rsupost_raises_on_http_error(rsu):
    fake_resp = Mock(status_code=500, url='https://api.runsignup.com/rest/race/1/coupons')
    rsu.session.post = Mock(return_value=fake_resp)

    with pytest.raises(accessError):
        rsu._rsupost('https://api.runsignup.com/rest/race/1/coupons')


def test_rsupost_raises_on_rsu_error_payload(rsu):
    fake_resp = Mock(status_code=200, url='https://api.runsignup.com/rest/race/1/coupons')
    fake_resp.json.return_value = {'error': {'error_code': 100, 'error_msg': 'bad request'}}
    rsu.session.post = Mock(return_value=fake_resp)

    with pytest.raises(accessError):
        rsu._rsupost('https://api.runsignup.com/rest/race/1/coupons')
