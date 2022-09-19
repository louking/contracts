'''
caching - summary caching for database tables
====================================================
'''

# standard
from time import time

# pypi
from flask import current_app
from loutilities.timeu import asctime, dt2epoch
from loutilities.transform import Transform

# homegrown
from .dbmodel import db, SponsorRace, SponsorRaceRegCache
from .runsignup import RunSignUp
from .version import __docversion__

ymd = asctime('%Y-%m-%d')
mdy = asctime('%m/%d/%Y')
regtime = asctime('%m/%d/%Y %H:%M')
getdate = lambda d: ymd.dt2asc(mdy.asc2dt(d.split(' ')[0]))

def update_raceregcache(race_id, onlyrecentevents=True):
    """update race registration cache
    
    NOTE: caller should wrap this with try/except, and must commit to database after call
    
    :param race_id: service provider id for race
    
    :return: events (https://runsignup.com/API/race/:race_id/GET "events" list converted to dict)
    """
    # set up transformation from RunSignUp format to database cache format
    rsudt = asctime('%m/%d/%Y %H:%M')
    xformmap = dict(
        registration_date   = lambda r: rsudt.asc2dt(r['registration_date']),
        last_modified_ts    = 'last_modified',
        first_name          = lambda r: r['user']['first_name'],
        last_name           = lambda r: r['user']['last_name'],
        email               = lambda r: r['user']['email'],
        gender              = lambda r: r['user']['gender'],
        dob                 = lambda r: ymd.asc2dt(r['user']['dob']) if r['user']['dob'] else None,
    )   
    xform = Transform(xformmap, sourceattr=False)
    
    # get info about race
    race = SponsorRace.query.filter_by(couponproviderid=race_id, display=True).one_or_none()
    
    # skip race if we have no api
    if not race:
        raise f'race not found for service provider id {race_id}'
    if race.couponprovider != 'RunSignUp':
        raise f'service provider for {race.race} must be RunSignUp'

    # track last time we updated cache
    cacheupdatets = int(time())

    # get events from service provider
    with RunSignUp(key=current_app.config['RSU_KEY'], secret=current_app.config['RSU_SECRET']) as rsu:
        # get race, event data from service provider
        events = rsu.getraceevents(race_id)
        
        # loop through all events for this race
        for event in events:
            # skip events which completed before the last time we updated the cache
            latestenddate = 0
            for regperiod in event['registration_periods']:
                thisregcloses = regtime.asc2epoch(regperiod['registration_closes'])
                if thisregcloses > latestenddate:
                    latestenddate = thisregcloses
                    
            if onlyrecentevents and race.cacheupdatets > latestenddate: continue
        
            # ok, we're processing an event
            current_app.logger.info(f'update_raceregcache(): processing {race.race} {event["name"]} {event["start_time"]}')
        
            # get participants updated since last registration update
            # NOTE: this includes the participants from the last second again, 
            # as it's possible there was a registration during the last second and we don't want to drop those
            participants = rsu.getraceparticipants(race.couponproviderid, event['event_id'], modified_after_timestamp=race.cacheupdatets)
            
            # add participant to cache, or update their entry
            for participant in participants:
                regid = participant['registration_id']
                thisparticipant = SponsorRaceRegCache.query.filter_by(registration_id=regid).one_or_none()
                if not thisparticipant:
                    thisparticipant = SponsorRaceRegCache(registration_id=regid)
                    db.session.add(thisparticipant)
                xform.transform(participant, thisparticipant)
                thisparticipant.event_id = event['event_id']
                thisparticipant.event_name = event['name']
                thisparticipant.is_active = True
                
            remparticipants = rsu.getremovedparticipants(race.couponproviderid, event['event_id'], modified_after_timestamp=race.cacheupdatets)
            
            # make removed participants inactive
            for participant in remparticipants:
                regid = participant['registration_id']
                thisparticipant = SponsorRaceRegCache.query.filter_by(registration_id=regid).one_or_none()
                
                if thisparticipant:
                    thisparticipant.is_active = False
                
                # this can happen if registration and transfer happened since last cache update
                else:
                    pass
                    # current_app.logger.warning(f'update_raceregcache(): registration id {regid} not found when removing registration from {race.race} {thisevent} {racedate}')
            
    # update timestamp for next cache update
    race.cacheupdatets = cacheupdatets

    # save the caller from contacting runsignup again
    return events
