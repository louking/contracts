###########################################################################################
# daterule - methods for manipulation of date rule object
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/13/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
daterule - methods for manipulation of date rule object
=========================================================
'''

# standard
from datetime import date, datetime, timedelta

# pypi
from dateutil.easter import easter
from dateutil.rrule import rrule
from dateutil.rrule import YEARLY, DAILY, SA, SU, MO, TU, WE, TH, FR

class parameterError(Exception): pass

# set up translation tables for some of the rules, days and months
rules = [ 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Last' ]
offsets = [1, 2, 3, 4, 5, -1]
rulex = dict( zip( rules, offsets ) )

days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
weekdays = [ SU, MO, TU, WE, TH, FR, SA ]
dayx = dict( zip( days, weekdays ) )

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthndxs = range(1,12+1)
monthx = dict( zip( months, monthndxs ) )

ONEDAY = timedelta(1)

#-------------------------------------------------------------------------
def daterule2dates(rule, year=None):
#-------------------------------------------------------------------------
    '''
    translate DateRule to dates for a given year

    parameters

    * rule - DateRule
    * year - year (ignored for rule with year specified), default current year
    '''
    if not year:
        year = date.today().year

    if rule.rule in rulex:
        theyear = date(year,1,1)
        month = monthx[ rule.month ]
        day = dayx[ rule.day ]
        offset = rulex[ rule.rule ]
        # rrule needs to be turned into a list. note there's only 1 in the list at this point
        thisdate = list( rrule( dtstart=theyear, freq=YEARLY, count=1, bymonth=month, byweekday=(day(offset) ) ) )[0]

    elif rule.rule == 'Easter':
        thisdate = easter( year )

    elif rule.rule == 'Date':
        if rule.year:
            year = rule.year
        thisdate = datetime( year, monthx[rule.month], rule.date )

    else:
        raise parameterError, 'invalid rule "{}"'.format(rule.rule)

    # handle deltaday
    if rule.deltaday:
        thisdate = thisdate + rule.deltaday * ONEDAY

    # transition to list
    thedates = [thisdate]

    # handle addldays
    if rule.addldays:
        direction = -1 if rule.addldays < 0 else 1
        for offset in range(direction, rule.addldays+direction, direction):
            thedates.append( thisdate + offset*ONEDAY )

    # only return date portion, sort to be polite
    thedates.sort()
    return [str(thedate).split(' ')[0] for thedate in thedates]