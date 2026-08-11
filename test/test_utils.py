'''
test_utils - test contracts.utils
=========================================================
'''

# pypi
import pytest

# homegrown
from contracts.utils import time24, renew_event, renew_sponsorship, parameterError
from contracts.dbmodel import (
    db, Race, Event, State, Tag, DateRule, Client,
    Sponsor, SponsorRace, SponsorTag,
    STATE_RENEWED_PENDING, TAG_RACERENEWED, SPONSORTAG_RACERENEWED,
)


# ----------------------------------------------------------------------
# time24
# ----------------------------------------------------------------------

def test_time24_no_time_returns_midnight():
    assert time24(None) == '00:00'
    assert time24('') == '00:00'


def test_time24_am_hour_below_12():
    assert time24('8:30 am') == '08:30'


def test_time24_am_12_becomes_00():
    assert time24('12:15 am') == '00:15'


def test_time24_pm_hour_below_12_adds_12():
    assert time24('8:30 pm') == '20:30'


def test_time24_pm_12_stays_12():
    assert time24('12:15 pm') == '12:15'


def test_time24_with_seconds():
    assert time24('1:02:03 pm') == '13:02:03'


def test_time24_invalid_field_count_raises():
    with pytest.raises(parameterError):
        time24('1 pm')


# ----------------------------------------------------------------------
# renew_event
# ----------------------------------------------------------------------

@pytest.fixture
def renewsetup(bare_dbapp):
    '''common db rows needed by renew_event/renew_sponsorship'''
    state = State(state=STATE_RENEWED_PENDING, description='renewed pending')
    renewedtag = Tag(tag=TAG_RACERENEWED, description='race renewed', isBuiltIn=True)
    sponsorrenewedtag = SponsorTag(tag=SPONSORTAG_RACERENEWED, description='sponsorship renewed', isBuiltIn=True)
    db.session.add_all([state, renewedtag, sponsorrenewedtag])
    db.session.commit()
    return {'state': state, 'renewedtag': renewedtag, 'sponsorrenewedtag': sponsorrenewedtag}


def test_renew_event_creates_daterule_when_none_exists(renewsetup):
    race = Race(race='Test Race')
    db.session.add(race)
    db.session.commit()

    # 2026-03-10 is the 2nd Tuesday of March 2026
    event = Event(date='2026-03-10', race=race, finishersCurrYear=100)
    db.session.add(event)
    db.session.commit()

    newevent = renew_event(event)
    db.session.commit()

    assert race.daterule is not None
    assert race.daterule.rule == 'Second'
    assert race.daterule.day == 'Tue'
    assert race.daterule.month == 'Mar'

    # next year's 2nd Tuesday of March 2027 is 2027-03-09
    assert newevent.date == '2027-03-09'
    assert newevent.state.state == STATE_RENEWED_PENDING
    assert newevent.finishersPrevYear == 100
    assert newevent.maxParticipants == 100
    assert newevent.finishersCurrYear is None
    assert renewsetup['renewedtag'] in event.tags


def test_renew_event_reuses_existing_daterule_with_same_rulename(renewsetup):
    daterule = DateRule(rule='Second', day='Tue', month='Mar')
    race = Race(race='Test Race', daterule=daterule)
    db.session.add(race)
    db.session.commit()

    event = Event(date='2026-03-10', race=race)
    db.session.add(event)
    db.session.commit()

    renew_event(event)
    db.session.commit()

    # no duplicate daterule created
    assert DateRule.query.filter_by(rulename=daterule.rulename).count() == 1
    assert race.daterule_id == daterule.id


def test_renew_event_clears_contract_fields_on_new_event(renewsetup):
    daterule = DateRule(rule='Second', day='Tue', month='Mar')
    race = Race(race='Test Race', daterule=daterule)
    event = Event(date='2026-03-10', race=race, contractSentDate='2026-01-01',
                  contractSignedDate='2026-01-05', notes='old notes',
                  isContractUpdated=True, isInvoiceInitiated=True)
    db.session.add(event)
    db.session.commit()

    newevent = renew_event(event)
    db.session.commit()

    assert newevent.contractSentDate is None
    assert newevent.contractSignedDate is None
    assert newevent.notes is None
    assert newevent.isContractUpdated is False
    assert newevent.isInvoiceInitiated is False


def test_renew_event_already_renewed_finds_next_event(renewsetup):
    daterule = DateRule(rule='Second', day='Tue', month='Mar')
    race = Race(race='Test Race', daterule=daterule)
    event = Event(date='2026-03-10', race=race)
    event.tags.append(renewsetup['renewedtag'])
    laterevent = Event(date='2027-03-09', race=race)
    db.session.add_all([event, laterevent])
    db.session.commit()

    result = renew_event(event)

    assert result.id == laterevent.id


# ----------------------------------------------------------------------
# renew_sponsorship
# ----------------------------------------------------------------------

def test_renew_sponsorship_creates_new_sponsorship(renewsetup):
    sponsorrace = SponsorRace(race='Test Sponsor Race')
    client = Client(client='Acme Inc', contactFirstName='Jo', contactLastName='Smith')
    db.session.add_all([sponsorrace, client])
    db.session.commit()

    sponsorship = Sponsor(raceyear=2026, amount=500, race=sponsorrace, client=client,
                          datesolicited='2026-01-01', couponcode='ABC123')
    db.session.add(sponsorship)
    db.session.commit()

    [newsponsorship] = renew_sponsorship(sponsorship)
    db.session.commit()

    assert newsponsorship.raceyear == 2027
    assert newsponsorship.state.state == STATE_RENEWED_PENDING
    assert newsponsorship.datesolicited is None
    assert newsponsorship.couponcode is None
    assert newsponsorship.isWebsiteUpdated is False
    assert newsponsorship.RegSiteUpdated == 'no'
    assert newsponsorship.trend == 'pending'
    assert renewsetup['sponsorrenewedtag'] in sponsorship.tags


def test_renew_sponsorship_already_renewed_finds_later_sponsorships(renewsetup):
    sponsorrace = SponsorRace(race='Test Sponsor Race')
    client = Client(client='Acme Inc', contactFirstName='Jo', contactLastName='Smith')
    db.session.add_all([sponsorrace, client])
    db.session.commit()

    sponsorship = Sponsor(raceyear=2026, amount=500, race=sponsorrace, client=client)
    sponsorship.tags.append(renewsetup['sponsorrenewedtag'])
    latersponsorship = Sponsor(raceyear=2027, amount=500, race=sponsorrace, client=client)
    db.session.add_all([sponsorship, latersponsorship])
    db.session.commit()

    result = renew_sponsorship(sponsorship)

    assert [s.id for s in result] == [latersponsorship.id]
