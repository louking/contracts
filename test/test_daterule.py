'''
test_daterule - test contracts.daterule
=========================================================
'''

# pypi
import pytest

# homegrown
from contracts.daterule import daterule2dates, date2daterule, parameterError
from contracts.dbmodel import DateRule


def test_daterule2dates_nth_weekday_of_month():
    # 2nd Tuesday of March 2026 is 2026-03-10
    rule = DateRule(rule='Second', day='Tue', month='Mar')
    assert daterule2dates(rule, 2026) == ['2026-03-10']


def test_daterule2dates_last_weekday_of_month():
    # last Monday of May 2026 is 2026-05-25
    rule = DateRule(rule='Last', day='Mon', month='May')
    assert daterule2dates(rule, 2026) == ['2026-05-25']


def test_daterule2dates_easter():
    rule = DateRule(rule='Easter')
    # Easter 2026 is 2026-04-05
    assert daterule2dates(rule, 2026) == ['2026-04-05']


def test_daterule2dates_fixed_date_uses_supplied_year():
    rule = DateRule(rule='Date', month='Jul', date=4)
    assert daterule2dates(rule, 2026) == ['2026-07-04']


def test_daterule2dates_fixed_date_with_own_year_ignores_supplied_year():
    rule = DateRule(rule='Date', month='Jul', date=4, year=2020)
    assert daterule2dates(rule, 2026) == ['2020-07-04']


def test_daterule2dates_default_year_is_current_year():
    from datetime import date
    rule = DateRule(rule='Easter')
    thisyear = date.today().year
    [result] = daterule2dates(rule)
    assert result.startswith(str(thisyear))


def test_daterule2dates_deltaday_shifts_date():
    # Sunday before the 2nd Tuesday of March 2026 (2026-03-10) is 2026-03-08 (deltaday=-2)
    rule = DateRule(rule='Second', day='Tue', month='Mar', deltaday=-2)
    assert daterule2dates(rule, 2026) == ['2026-03-08']


def test_daterule2dates_addldays_positive_appends_following_days():
    rule = DateRule(rule='Second', day='Tue', month='Mar', addldays=2)
    assert daterule2dates(rule, 2026) == ['2026-03-10', '2026-03-11', '2026-03-12']


def test_daterule2dates_addldays_negative_prepends_preceding_days():
    rule = DateRule(rule='Second', day='Tue', month='Mar', addldays=-2)
    assert daterule2dates(rule, 2026) == ['2026-03-08', '2026-03-09', '2026-03-10']


def test_daterule2dates_invalid_rule_raises():
    rule = DateRule(rule=None)
    rule.rule = 'bogus'
    with pytest.raises(parameterError):
        daterule2dates(rule, 2026)


def test_date2daterule_builds_matching_rule():
    # 2026-03-10 is the 2nd Tuesday of March 2026
    result = date2daterule('2026-03-10')
    assert isinstance(result, DateRule)
    assert result.rule == 'Second'
    assert result.day == 'Tue'
    assert result.month == 'Mar'


def test_date2daterule_last_week_of_month():
    # 2026-05-25 falls in the 5th week (day // 7 == 3 -> 'Fourth'), per date2daterule's own logic
    result = date2daterule('2026-05-25')
    assert result.day == 'Mon'
    assert result.month == 'May'


def test_daterule2dates_roundtrips_date2daterule_for_nth_weekday_rules():
    # date2daterule always derives 'Nth' rules (never 'Last'), so round-tripping through
    # daterule2dates for the same year should reproduce the original date
    original = '2026-03-10'
    rule = date2daterule(original)
    assert daterule2dates(rule, 2026) == [original]
