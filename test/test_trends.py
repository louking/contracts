'''
test_trends - test contracts.trends
=========================================================
'''

# pypi
import pytest
from dominate.tags import li

# homegrown
from contracts.trends import calculateTrend, check_sponsorship_conflicts, render_sponsorship_conflicts
from contracts.dbmodel import (
    db, Sponsor, SponsorRace, Client, State,
    STATE_COMMITTED, STATE_CONTRACT_SENT, STATE_CANCELED, STATE_TENTATIVE, STATE_RENEWED_PENDING,
)


@pytest.fixture
def states(bare_dbapp):
    states = {
        s: State(state=s, description=s)
        for s in [STATE_COMMITTED, STATE_CONTRACT_SENT, STATE_CANCELED, STATE_TENTATIVE, STATE_RENEWED_PENDING]
    }
    db.session.add_all(states.values())
    db.session.commit()
    return states


@pytest.fixture
def race_and_client(states):
    race = SponsorRace(race='Test Sponsor Race')
    client = Client(client='Acme Inc', contactFirstName='Jo', contactLastName='Smith')
    db.session.add_all([race, client])
    db.session.commit()
    return race, client


def make_sponsor(race, client, raceyear, amount, state, statename=None):
    sponsor = Sponsor(race=race, client=client, raceyear=raceyear, amount=amount, state=state)
    db.session.add(sponsor)
    db.session.commit()
    return sponsor


# ----------------------------------------------------------------------
# calculateTrend
# ----------------------------------------------------------------------

def test_calculateTrend_new_when_no_prior_year(states, race_and_client):
    race, client = race_and_client
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])

    calculateTrend([sponsor])

    assert sponsor.trend == 'new'


def test_calculateTrend_same_amount(states, race_and_client):
    race, client = race_and_client
    make_sponsor(race, client, 2025, 500, states[STATE_COMMITTED])
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])

    calculateTrend([sponsor])

    assert sponsor.trend == 'same'


def test_calculateTrend_up(states, race_and_client):
    race, client = race_and_client
    make_sponsor(race, client, 2025, 300, states[STATE_COMMITTED])
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])

    calculateTrend([sponsor])

    assert sponsor.trend == 'up'


def test_calculateTrend_down(states, race_and_client):
    race, client = race_and_client
    make_sponsor(race, client, 2025, 800, states[STATE_COMMITTED])
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])

    calculateTrend([sponsor])

    assert sponsor.trend == 'down'


def test_calculateTrend_lost_for_canceled(states, race_and_client):
    race, client = race_and_client
    make_sponsor(race, client, 2025, 500, states[STATE_COMMITTED])
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_CANCELED])

    calculateTrend([sponsor])

    assert sponsor.trend == 'lost'


def test_calculateTrend_solicited_for_tentative(states, race_and_client):
    race, client = race_and_client
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_TENTATIVE])

    calculateTrend([sponsor])

    assert sponsor.trend == 'solicited'


def test_calculateTrend_pending_for_renewed_pending(states, race_and_client):
    race, client = race_and_client
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_RENEWED_PENDING])

    calculateTrend([sponsor])

    assert sponsor.trend == 'pending'


def test_calculateTrend_recurses_to_next_year(states, race_and_client):
    race, client = race_and_client
    sponsor = make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])
    nextyear = make_sponsor(race, client, 2027, 500, states[STATE_COMMITTED])

    calculateTrend([sponsor])

    # next year's trend gets calculated too, as a side effect of the recursive call
    assert nextyear.trend == 'same'


# ----------------------------------------------------------------------
# check_sponsorship_conflicts / render_sponsorship_conflicts
# ----------------------------------------------------------------------

def test_check_sponsorship_conflicts_detects_multiple_states(states, race_and_client):
    race, client = race_and_client
    make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])
    make_sponsor(race, client, 2026, 500, states[STATE_TENTATIVE])

    sponsorships = Sponsor.query.all()
    errors = check_sponsorship_conflicts(sponsorships)

    assert len(errors) == 1
    html = errors[0].render()
    assert 'year=2026' in html
    assert STATE_COMMITTED in html
    assert STATE_TENTATIVE in html


def test_check_sponsorship_conflicts_no_conflict_for_single_state(states, race_and_client):
    race, client = race_and_client
    make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])
    make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])

    sponsorships = Sponsor.query.all()
    errors = check_sponsorship_conflicts(sponsorships)

    assert errors == []


def test_check_sponsorship_conflicts_ignores_canceled_and_zero_amount(states, race_and_client):
    race, client = race_and_client
    make_sponsor(race, client, 2026, 500, states[STATE_COMMITTED])
    make_sponsor(race, client, 2026, 500, states[STATE_CANCELED])
    make_sponsor(race, client, 2026, 0, states[STATE_TENTATIVE])

    sponsorships = Sponsor.query.all()
    errors = check_sponsorship_conflicts(sponsorships)

    assert errors == []


def test_render_sponsorship_conflicts_wraps_error_items():
    errors = [li('year=2026 race="Test Race" client="Acme": committed, tentative')]

    html = render_sponsorship_conflicts(errors)

    assert 'Sponsor client with multiple sponsorships' in html
    assert 'year=2026 race=' in html
    assert 'committed, tentative' in html
