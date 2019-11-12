###########################################################################################
# trends - manage trends
#
#   Date        Author          Reason
#   ----        ------          ------
#   04/24/19    Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
trends - manage trends
================================================
'''

# pypi
from flask import current_app

# homegrown
from contracts.dbmodel import db, Sponsor
from contracts.dbmodel import STATE_COMMITTED, STATE_CANCELED, STATE_TENTATIVE, STATE_RENEWED_PENDING

debug = True

#----------------------------------------------------------------------
def calculateTrend(thisyeardb):
#----------------------------------------------------------------------
    '''
    calculate and updated trend in a sponsor record. caller must commit db changes.

    :param thisyeardb: Sponsor record
    '''
    # *** note the logic here must match that in sponsor-summary.js ***

    thisyear = int(thisyeardb.raceyear)
    race_id = thisyeardb.race_id
    client_id = thisyeardb.client_id
    prevyeardb = Sponsor.query.filter(Sponsor.race_id==race_id, Sponsor.raceyear==thisyear-1, Sponsor.client_id==client_id, Sponsor.amount>0).one_or_none()
    nextyeardb = Sponsor.query.filter(Sponsor.race_id==race_id, Sponsor.raceyear==thisyear+1, Sponsor.client_id==client_id, Sponsor.amount>0).one_or_none()

    # new or potentially new sponsorship
    if not prevyeardb or prevyeardb.state.state != STATE_COMMITTED:
        thisyeardb.trend = 'new'

    # last year exists and was committed
    else:
        thisamount = int(thisyeardb.amount)
        prevamount = int(prevyeardb.amount)
        if debug: current_app.logger.debug('calculateTrend(): year={} thisyear.amount={} prevyear.amount={}'.format(
            thisyeardb.raceyear, thisamount, prevamount
            ))
        if thisyeardb.state.state == STATE_COMMITTED:
            if thisamount == prevamount:
                thisyeardb.trend = 'same'

            elif thisamount > prevamount:
                thisyeardb.trend = 'up'

            elif thisamount < prevamount:
                thisyeardb.trend = 'down'

        elif thisyeardb.state.state == STATE_CANCELED:
            thisyeardb.trend = 'lost'

    if thisyeardb.state.state == STATE_TENTATIVE:
        thisyeardb.trend = 'solicited'

    elif thisyeardb.state.state == STATE_RENEWED_PENDING:
        thisyeardb.trend = 'pending'

    # maybe we're adding an old year, need to update the following year
    if nextyeardb:
        calculateTrend(nextyeardb)

    if debug: current_app.logger.debug('calculateTrend(): race="{}" year={} client="{}" trend={}'.format(
            thisyeardb.race.race, thisyeardb.raceyear, thisyeardb.client.client, thisyeardb.trend
        ))

