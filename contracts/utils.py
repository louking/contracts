###########################################################################################
# utils - miscellaneous utilities
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/19/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
utils - miscellaneous utilities
=======================================================================
'''

# pypi
from flask import current_app
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy import and_

# homegrown
from contracts.dbmodel import db, Event, Tag, DateRule, State
from contracts.dbmodel import Sponsor, SponsorTag, SPONSORTAG_RACERENEWED
from contracts.dbmodel import STATE_COMMITTED, STATE_RENEWED_PENDING, TAG_RACERENEWED
from contracts.daterule import date2daterule, daterule2dates

class parameterError(Exception): pass

#----------------------------------------------------------------------
def time24(time):
#----------------------------------------------------------------------
    '''
    calculate 24 hour time

    :param time: [h]h:mm[:ss] [a]m
    :rtype: hh:mm[:ss]
    '''
    # handle case of no time supplied
    if not time: return '00:00'

    # split out ampm (see events.py datetime format 'h:mm a')
    thetime, ampm = time.split(' ')

    # split time into fields h:m[:s]
    fields = [int(t) for t in thetime.split(':')]

    # hopefully this error was detected before time was put into database
    if len(fields) < 2 or len(fields) > 3:
        raise parameterError('invalid time field {} detected'.format(time))
    
    # use 24 hour clock
    if ampm.lower() == 'pm' and fields[0] != 12:
        fields[0] += 12
    if ampm.lower() == 'am' and fields[0] == 12:
        fields[0] -= 12
    
    # build and return string hh:mm[:ss]
    fieldstrs = []
    for field in fields:
        fieldstrs.append(str(field).zfill(2))
    return ':'.join(fieldstrs)

#----------------------------------------------------------------------
def renew_event(event):
#----------------------------------------------------------------------
    '''
    renew event based on event.race.daterule

    if daterule doesn't exist, create it assuming nth dow month

    caller needs to commit the database update, or roll back

    :param event: event to renew

    :rtype: new event from renew process
    '''
    # set up tag to indicate event was renewed
    renewedtag = Tag.query.filter_by(tag=TAG_RACERENEWED).one()

    # don't renew the race twice
    if renewedtag not in event.tags: 

        # if date rule now present, create based on nth dow month
        if not event.race.daterule:
            newdaterule = date2daterule(event.date)
            daterule = DateRule.query.filter_by(rulename=newdaterule.rulename).one_or_none()
            
            # create daterule if it's not in database yet
            if not daterule:
                db.session.add(newdaterule)
                daterule = newdaterule

            # update race's date rule
            event.race.daterule = daterule

        # create new event based on this event's daterule
        neweventdict = {k:v for k,v in list(event.__dict__.items()) if k[0] != '_' and k != 'id'}
        newevent = Event(**neweventdict)
        
        # the following assumes only one date will be returned from the event's date rule
        curryr,mo,day = event.date.split('-')
        thedates = daterule2dates(event.race.daterule, int(curryr)+1)
        newevent.date = thedates[0]

        # update fields within the new event to start fresh
        newevent.state = State.query.filter_by(state=STATE_RENEWED_PENDING).one()
        
        # hopefully admin put something in finishersCurrYear, otherwise these will be cleared
        newevent.finishersPrevYear = event.finishersCurrYear
        newevent.maxParticipants = event.finishersCurrYear
        newevent.finishersCurrYear = None

        # clear the contract fields and other fields we want to start empty
        newevent.tags = []
        for f in ['contractSentDate', 'contractSignedDate', 'invoiceSentDate', 'isOnCalendar', 'contractDocId', 
                  'notes', 'contractApprover', 'contractApproverEmail', 'contractApproverNotes', 'lead']:
            setattr(newevent, f, None)

        # renewed race contract has not been updated yet
        newevent.isContractUpdated = False
        
        # make sure services are carried over
        for service in event.services:
            newevent.services.append(service)

        # make sure addons are carried over
        for addon in event.addOns:
            newevent.addOns.append(addon)
            
        # add the new event to the database
        db.session.add(newevent)

        # current event has been renewed
        event.tags.append(renewedtag)

    # determine the renewal event if race had already been renewed
    else:
        # find all events with this race id after the current event date
        # really should only be one
        start = event.date
        try:
            newevent = Event.query.filter(Event.race_id == event.race_id).filter(Event.date > start).one_or_none()

        # well this shouldn't have happened. Just return the first we fine
        except MultipleResultsFound:
            current_app.logger.error('renew_event(): multiple renewed events found for {} {}'.format(event.date, event.race.race))
            events = Event.query.filter_by(race_id=event.race_id).filter(Event.date > start).all()
            newevent = events[0]

    return newevent


# ----------------------------------------------------------------------
def renew_sponsorship(sponsorship):
    # ----------------------------------------------------------------------
    '''
    renew sponsorship

    caller needs to commit the database update, or roll back

    :param sponsorship: sponsorship to renew

    :rtype: sponsorships from renew process (list)
    '''
    # set up tag to indicate event was renewed
    renewedtag = SponsorTag.query.filter_by(tag=SPONSORTAG_RACERENEWED).one()

    # don't renew the sponsorship twice
    if renewedtag not in sponsorship.tags:

        # create new sponsorship based on this sponsorship's daterule
        newsponsorshipdict = {k: v for k, v in list(sponsorship.__dict__.items()) if k[0] != '_' and k != 'id'}
        newsponsorship = Sponsor(**newsponsorshipdict)

        # update fields within the new sponsorship to start fresh
        newsponsorship.state = State.query.filter_by(state=STATE_RENEWED_PENDING).one()

        # bump the raceyear
        newsponsorship.raceyear = sponsorship.raceyear+1

        # reset the sponsorship fields and other fields we want fixed values for
        for f in ['datesolicited', 'dateagreed', 'invoicesent', 'couponcode',
                  'contractDocId', 'notes' ]:
            setattr(newsponsorship, f, None)

        for f in ['isWebsiteUpdated', 'isSponsorThankedFB']:
            setattr(newsponsorship, f, False)

        newsponsorship.tags = []
        newsponsorship.RegSiteUpdated = 'no'
        newsponsorship.trend = 'pending'

        # add the new sponsorship to the database
        db.session.add(newsponsorship)

        # current sponsorship has been renewed
        sponsorship.tags.append(renewedtag)
        
        newsponsorships = [newsponsorship]

    # determine the renewal sponsorships if race had already been renewed
    else:
        # find all sponsorships with this race id after the current sponsorship date
        thisraceyear = sponsorship.raceyear
        newsponsorships = Sponsor.query.filter(and_(Sponsor.race_id == sponsorship.race_id,
                                                    Sponsor.client_id == sponsorship.client_id,
                                                    Sponsor.raceyear > thisraceyear)).all()

    return newsponsorships