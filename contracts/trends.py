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
from dominate.tags import div, p, ul, li

# homegrown
from .dbmodel import Sponsor
from .dbmodel import STATE_COMMITTED, STATE_CONTRACT_SENT, STATE_CANCELED, STATE_TENTATIVE, STATE_RENEWED_PENDING

debug = True

#----------------------------------------------------------------------
def calculateTrend(thisyearsships):
#----------------------------------------------------------------------
    '''
    calculate and update trend in a sponsor record. caller must commit db changes.

    :param thisyearsships: Sponsor records for this client / race / year
    '''
    # *** note the logic here must match that in sponsor-summary.js ***

    thisyear = int(thisyearsships[0].raceyear)
    race_id = thisyearsships[0].race_id
    client_id = thisyearsships[0].client_id
    prevyearsships = [s for s in Sponsor.query.filter(Sponsor.race_id==race_id, Sponsor.raceyear==thisyear-1, Sponsor.client_id==client_id, Sponsor.amount>0).all()
                      if s.state.state == STATE_COMMITTED]
    nextyearsships = Sponsor.query.filter(Sponsor.race_id==race_id, Sponsor.raceyear==thisyear+1, Sponsor.client_id==client_id, Sponsor.amount>0).all()

    # new or potentially new sponsorship
    if not prevyearsships:
        for thissship in thisyearsships:
            thissship.trend = 'new'

    # last year exists and was committed
    else:
        thisamount = sum([int(s.amount) for s in thisyearsships])
        prevamount = sum([int(s.amount) for s in prevyearsships])
        if debug: current_app.logger.debug(f'calculateTrend(): year={thisyear} thisyear.amount={thisamount} prevyear.amount={prevamount}')
        for thisyearsship in thisyearsships:
            # NOTE: STATE_CONTRACT_SENT isn't possible for sponsors, but is covered here for completeness
            if thisyearsship.state.state in [STATE_COMMITTED, STATE_CONTRACT_SENT]:
                if thisamount == prevamount:
                    thisyearsship.trend = 'same'

                elif thisamount > prevamount:
                    thisyearsship.trend = 'up'

                elif thisamount < prevamount:
                    thisyearsship.trend = 'down'

            elif thisyearsship.state.state == STATE_CANCELED:
                thisyearsship.trend = 'lost'

    for thisyearsship in thisyearsships:
        if thisyearsship.state.state == STATE_TENTATIVE:
            thisyearsship.trend = 'solicited'

        elif thisyearsship.state.state == STATE_RENEWED_PENDING:
            thisyearsship.trend = 'pending'

    # maybe we're adding an old year, need to update the following year
    if nextyearsships:
        calculateTrend(nextyearsships)

    if debug: 
        for s in thisyearsships:
            current_app.logger.debug(f'calculateTrend(): race="{s.race.race}" year={s.raceyear} client="{s.client.client}" trend={s.trend} id={s.id}')

def render_sponsorship_conflicts(error_list):
    """generate html for sponsorship conflicts

    Args:
        error_list (list): list of dominate li tags with conflicts

    Returns:
        str: html to be shown to user
    """
    error_d = div()
    with error_d:
        p(f'Sponsor client with multiple sponsorships found to have inconsistent states -- if not fixed, Sponsorship Summary view may show invalid results')
        ul(error_list)
    error_html = error_d.render()
    return error_html
            
def check_sponsorship_conflicts(sponsorships):
    """check for sponsorship state inconsistencies in list of sponsorships

    Args:
        sponsorships ([Sponsor, ...]): list of sponsorships (Sponsor records) to check

    Returns:
        list of dominate.tags.li: li elements for state errors, empty list if no errors found
    """
    # we don't care about canceled sponsorships or those with no $ amount (probably in-kind)
    relevantsships = [s for s in sponsorships if s.state.state != STATE_CANCELED and s.amount != 0]
    
    # build structure by year, race, client
    yrc = {}
    for sship in relevantsships:
        year = yrc.setdefault(sship.raceyear, {})
        race = year.setdefault(sship.race_id, {})
        sships = race.setdefault(sship.client_id, [])
        sships.append(sship)
    
    error_list = []
    
    years = list(yrc.keys())
    years.sort
    for y in years:
        races = list(yrc[y].keys())
        races.sort()
        for r in races:
            clients = list(yrc[y][r].keys())
            clients.sort()
            for c in clients:
                sponsorships = yrc[y][r][c]
                states = set([s.state.state for s in sponsorships])
                # more than one state found in the sponsorship list means there are incompatible states
                # NOTE: STATE_CONTRACT_SENT (equivalent to STATE_COMMITTED) isn't possible for race sponsors
                if len(states) > 1:
                    thisrace = sponsorships[0].race.race
                    thisclient = sponsorships[0].client.client
                    error_list.append(li(f'year={y} race="{thisrace}" client="{thisclient}": {", ".join(states)}'))
    
    return error_list
