'''
contract_tasks - background tasks needed for contract event management
=======================================================================

'''
# standard
from copy import deepcopy
from datetime import date, timedelta
from urllib.parse import quote_plus
from re import match

# pypi
from flask import current_app
from flask.cli import with_appcontext
from jinja2 import Template
from click import argument, group

# homegrown
from contracts import create_app
from contracts.dbmodel import db, Event, Contract, ContractType, TemplateType, Tag, State
from contracts.dbmodel import Sponsor, SponsorRaceDate
from contracts.dbmodel import TAG_PRERACEMAILSENT, TAG_PRERACEMAILINHIBITED
from contracts.dbmodel import TAG_BIBCOUNTMAILSENT, TAG_BIBCOUNTMAILINHIBITED
from contracts.dbmodel import TAG_POSTRACEMAILSENT, TAG_POSTRACEMAILINHIBITED
from contracts.dbmodel import TAG_PRERACEPREMPROMOEMAILSENT, TAG_PRERACEPREMPROMOEMAILINHIBITED
from contracts.dbmodel import TAG_LEADEMAILSENT
from contracts.dbmodel import TAG_PRERACERENEWEDREMINDEREMAILSENT, TAG_PRERACERENEWEDCANCELED
from contracts.dbmodel import STATE_COMMITTED, STATE_RENEWED_PENDING, STATE_CANCELED
from loutilities.flask_helpers.mailer import sendmail
from contracts.utils import renew_event, renew_sponsorship
from loutilities.timeu import asctime

from scripts import catch_errors, ParameterError

# set up datatabase date formatter
dbdate = asctime('%Y-%m-%d')

# debug
debug = False

# needs to be before any commands
@group()
def contract():
    """Perform contract related tasks"""
    pass

@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def preraceemail(startdate, enddate):
    '''Send pre-race email to race director and lead.'''

    # set up tag which is used to control this email
    senttag = Tag.query.filter_by(tag=TAG_PRERACEMAILSENT).one()
    inhibittag = Tag.query.filter_by(tag=TAG_PRERACEMAILINHIBITED).one()

    # calculate start and end date window
    if startdate == 'auto' and enddate == 'auto':
        # calculate start and end date window
        start = dbdate.dt2asc(date.today())
        end = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_PRERACE_EMAIL']))

    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate == 'auto' or enddate == 'auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
                not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # use correct filter to get races in next N days
    events = Event.query.filter(Event.date.between(start, end)).all()

    for event in events:
        # ignore uncommitted events
        if event.state.state != STATE_COMMITTED: continue

        # don't send if this message has already been sent or was inhibited by admin
        if senttag in event.tags or inhibittag in event.tags: continue

        # don't send if only premium promotion service
        if len(event.services) == 1 and event.services[0].service == 'premiumpromotion': continue

        # send pre-race mail to client
        templatestr = (db.session.query(Contract)
                   .filter(Contract.contractTypeId==ContractType.id)
                   .filter(ContractType.contractType=='race services')
                   .filter(Contract.templateTypeId==TemplateType.id)
                   .filter(TemplateType.templateType=='pre-race email')
                   .one()
                  ).block
        template = Template( templatestr )

        # bring in needed relations
        garbage = event.client
        garbage = event.lead
        garbage = event.course

        # merge database fields into template and send email
        mergefields = deepcopy(event.__dict__)
        docid = event.contractDocId

        mergefields['viewcontracturl'] = 'https://docs.google.com/document/d/{}/view'.format(docid)
        mergefields['servicenames'] = [s.service for s in event.services] 
        mergefields['event'] = event.race.race

        html = template.render( mergefields )

        subject = 'FSRC Pre-race Coordination: {} - {}'.format(event.race.race, event.date)
        tolist = event.client.contactEmail
        cclist = current_app.config['CONTRACTS_CC'] + [event.lead.email]
        fromlist = current_app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        event.tags.append(senttag)
        db.session.commit()

@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def chipcountemail(startdate, enddate):
    '''Send bib count request email to race director and lead.'''

    # set up tag which is used to control this email
    senttag = Tag.query.filter_by(tag=TAG_BIBCOUNTMAILSENT).one()
    inhibittag = Tag.query.filter_by(tag=TAG_BIBCOUNTMAILINHIBITED).one()

    # calculate start and end date window
    if startdate == 'auto' and enddate == 'auto':
        # calculate start and end date window
        start = dbdate.dt2asc(date.today())
        end = dbdate.dt2asc(date.today() 
                            + timedelta(current_app.config['DAYS_PRE_BIBCOUNT_REQUIRED_EMAIL'] 
                                        + current_app.config['DAYS_PRERACE_BIBCOUNT_REQUIRED']))

    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate == 'auto' or enddate == 'auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
                not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # use correct filter to get races in next N days
    events = Event.query.filter(Event.date.between(start, end)).all()

    for event in events:
        # ignore uncommitted events
        if event.state.state != STATE_COMMITTED: continue

        # don't send if this message has already been sent or was inhibited by admin
        if senttag in event.tags or inhibittag in event.tags: continue

        # don't send if not chip service service
        if 'chiptiming' not in [e.service for e in event.services]: continue

        # send bib count mail to client
        templatestr = (db.session.query(Contract)
                   .filter(Contract.contractTypeId==ContractType.id)
                   .filter(ContractType.contractType=='race services')
                   .filter(Contract.templateTypeId==TemplateType.id)
                   .filter(TemplateType.templateType=='bib count email')
                   .one()
                  ).block
        template = Template( templatestr )

        # bring in needed relations
        garbage = event.client
        garbage = event.lead
        garbage = event.course

        # merge database fields into template and send email
        mergefields = deepcopy(event.__dict__)
        docid = event.contractDocId

        mergefields['viewcontracturl'] = f'https://docs.google.com/document/d/{docid}/view'
        mergefields['downloadcontracturl'] = f'https://docs.google.com/document/d/{docid}/export?format=pdf'
        mergefields['servicenames'] = [s.service for s in event.services] 
        mergefields['event'] = event.race.race
        mergefields['chipcountdate'] = dbdate.dt2asc(dbdate.asc2dt(event.date) - timedelta(current_app.config['DAYS_PRERACE_BIBCOUNT_REQUIRED']))

        html = template.render( mergefields )

        subject = f'FSRC Bib Count Query: {event.race.race} - {event.date}'
        tolist = event.client.contactEmail
        cclist = current_app.config['CONTRACTS_CC'] + [event.lead.email]
        fromlist = current_app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        event.tags.append(senttag)
        db.session.commit()

@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def leademail(startdate, enddate):
    '''Send pre-race email to lead.'''

    # set up tag which is used to control this email
    senttag = Tag.query.filter_by(tag=TAG_LEADEMAILSENT).one()

    # calculate start and end date window
    if startdate == 'auto' and enddate == 'auto':
        # only send for races coming up within DAYS_LEAD_EMAIL in advance of the event,
        # but if it doesn't happen for some reason will retry until event passed
        start = dbdate.dt2asc(date.today())
        end = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_LEAD_EMAIL']))

    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate == 'auto' or enddate == 'auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
                not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # use correct filter to get races in next N days
    events = Event.query.filter(Event.date.between(start, end)).all()

    for event in events:
        # ignore uncommitted events
        if event.state.state != STATE_COMMITTED: continue

        # don't send if this message has already been sent
        if senttag in event.tags: continue

        # don't send if only premium promotion service
        if len(event.services) == 1 and event.services[0].service == 'premiumpromotion': continue

        # send pre-race mail to client
        templatestr = (db.session.query(Contract)
                   .filter(Contract.contractTypeId==ContractType.id)
                   .filter(ContractType.contractType=='race services')
                   .filter(Contract.templateTypeId==TemplateType.id)
                   .filter(TemplateType.templateType=='lead email')
                   .one()
                  ).block
        template = Template( templatestr )

        # bring in needed relations
        garbage = event.client
        garbage = event.lead
        garbage = event.course

        # merge database fields into template and send email
        mergefields = deepcopy(event.__dict__)

        mergefields['servicedescrs'] = [s.serviceLong for s in event.services if s.service != 'premiumpromotion']
        mergefields['addlservices'] = [a.longDescr for a in event.addOns]
        mergefields['event'] = event.race.race

        html = template.render( mergefields )

        subject = 'FSRC race reminders for lead: {} - {}'.format(event.race.race, event.date)
        tolist = event.lead.email
        cclist = current_app.config['CONTRACTS_CC']
        fromlist = current_app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        event.tags.append(senttag)
        db.session.commit()

@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def postraceprocessing(startdate, enddate):
    '''Sending post-race email and renew race.'''
    # set up tag which is used to control this email
    senttag = Tag.query.filter_by(tag=TAG_POSTRACEMAILSENT).one()
    inhibittag = Tag.query.filter_by(tag=TAG_POSTRACEMAILINHIBITED).one()

    if startdate == 'auto' and enddate == 'auto':
        # processing for races DAYS_POSTRACE_EMAIL days after the event,
        # but if it doesn't happen for some reason will retry for a week
        # calculate start and end date window (try to send for 1 week)
        start = dbdate.dt2asc(date.today() - timedelta(current_app.config['DAYS_POSTRACE_EMAIL'] + 7))
        end = dbdate.dt2asc(date.today() - timedelta(current_app.config['DAYS_POSTRACE_EMAIL']))

    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate == 'auto' or enddate == 'auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
                not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # use filter to get races in which occurred at least N days ago
    events = Event.query.filter(Event.date.between(start, end)).all()

    for event in events:
        # ignore uncommitted events
        if event.state.state != STATE_COMMITTED: continue

        # renew event
        newevent = renew_event(event)
        
        # pick up any db changes related to renewal (renew, daterule, event.tags)
        db.session.commit()

        # don't send email if this message has already been sent or was inhibited by admin
        # don't send email if only premium promotion service
        if senttag in event.tags or inhibittag in event.tags: continue
        if len(event.services) == 1 and event.services[0].service == 'premiumpromotion': continue

        # get post-race mail template
        templatestr = (db.session.query(Contract)
                   .filter(Contract.contractTypeId==ContractType.id)
                   .filter(ContractType.contractType=='race services')
                   .filter(Contract.templateTypeId==TemplateType.id)
                   .filter(TemplateType.templateType=='post-race email')
                   .one()
                  ).block
        template = Template( templatestr )

        # bring in needed relations
        garbage = event.client
        garbage = event.lead
        garbage = event.course

        # merge database fields into template and send email
        # deepcopy getting error AttributeError: 'Race' object has no attribute '_sa_instance_state'
        # so just collect what we need
        mergefields = deepcopy(event.__dict__)

        mergefields['nextyeartext'] = 'for next year'
        mergefields['servicenames'] = [s.service for s in event.services] 
        mergefields['event'] = event.race.race
        # this shouldn't happen, but need to handle case where renew_event couldn't find renewed race
        mergefields['renew_date'] = newevent.date if newevent else '[oops - an error occurred determining race date, please contact us]'

        surveyfields = {
            'eventencoded' : quote_plus(event.race.race),
            'dateencoded'  : quote_plus(event.date),
        }
        surveytemplate = Template( current_app.config['CONTRACTS_SURVEY_URL'] )
        mergefields['surveylink'] = surveytemplate.render( surveyfields )

        html = template.render( mergefields )

        subject = 'Thank You for using FSRC Race Support Services - {}'.format(event.date)
        tolist = event.client.contactEmail
        cclist = current_app.config['CONTRACTS_CC']
        fromlist = current_app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        event.tags.append(senttag)

        # pick up all db changes (event.tags)
        db.session.commit()

@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def preraceprempromoemail(startdate, enddate):
    '''Send pre-race premium promotion email.'''
    # set up tags which are used to control this email
    senttag = Tag.query.filter_by(tag=TAG_PRERACEPREMPROMOEMAILSENT).one()
    inhibittag = Tag.query.filter_by(tag=TAG_PRERACEPREMPROMOEMAILINHIBITED).one()

    # calculate start and end date window
    if startdate=='auto' and enddate=='auto':
        # only send for races within one week window
        # this causes sending DAYS_PRERACE_PREMPROMO_EMAIL in advance of the event, 
        # but if it doesn't happen for some reason will retry for a week
        start = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_PRERACE_PREMPROMO_EMAIL']) - timedelta(7))
        end = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_PRERACE_PREMPROMO_EMAIL']))
    
    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate=='auto' or enddate=='auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (  not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
              not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # debug
    # print 'start={} end={}'.format(start, end)

    # use filter to get races in which occurred at least N days ago
    events = Event.query.filter(Event.date.between(start, end)).all()

    for event in events:
        # ignore events unless they're in renewed-pending state
        if event.state.state != STATE_RENEWED_PENDING: continue

        # don't send email if this message has already been sent or was inhibited by admin
        # don't send email if other services are included or premiumpromotion not included
        if senttag in event.tags or inhibittag in event.tags: continue
        if len(event.services) > 1 or 'premiumpromotion' not in [s.service for s in event.services]: continue

        # get post-race mail template
        templatestr = (db.session.query(Contract)
                   .filter(Contract.contractTypeId==ContractType.id)
                   .filter(ContractType.contractType=='race services')
                   .filter(Contract.templateTypeId==TemplateType.id)
                   .filter(TemplateType.templateType=='prempromo email')
                   .one()
                  ).block
        template = Template( templatestr )

        # bring in needed relations
        garbage = event.client
        garbage = event.lead
        garbage = event.course

        # merge database fields into template and send email
        # deepcopy getting error AttributeError: 'Race' object has no attribute '_sa_instance_state'
        # so just collect what we need
        mergefields = deepcopy(event.__dict__)

        mergefields['event'] = event.race.race

        html = template.render( mergefields )

        subject = 'Frederick Steeplechasers Premium Promotion for {}'.format(event.race.race)
        tolist = event.client.contactEmail
        cclist = current_app.config['CONTRACTS_CC']
        fromlist = current_app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        event.tags.append(senttag)

        # pick up all db changes (event.tags)
        db.session.commit()


@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def latereminderemail(startdate, enddate):
    '''Send late renewed reminder email.'''
    # set up tags which are used to control this email
    senttag = Tag.query.filter_by(tag=TAG_PRERACERENEWEDREMINDEREMAILSENT).one()

    # calculate start and end date window
    if startdate == 'auto' and enddate == 'auto':
        # only send for races within one week window
        # this causes sending DAYS_PRERACE_LATEREMINDER_EMAIL in advance of the event,
        # but if it doesn't happen for some reason will retry for a week
        start = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_PRERACE_LATEREMINDER_EMAIL']) - timedelta(7))
        end = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_PRERACE_LATEREMINDER_EMAIL']))

    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate == 'auto' or enddate == 'auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
                not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # debug
    if debug: print('start={} end={}'.format(start, end))

    # use filter to get races in which occurred at least N days ago
    events = Event.query.filter(Event.date.between(start, end)).all()

    for event in events:
        # ignore events unless they're in renewed-pending state
        if event.state.state != STATE_RENEWED_PENDING: continue

        # don't send email if this message has already been sent or was inhibited by admin
        # don't send email if only premiumpromotion included (handled by another task)
        if senttag in event.tags: continue
        if len(event.services) == 1 and 'premiumpromotion' in [s.service for s in event.services]: continue

        # get late renewed reminder email template
        templatestr = (db.session.query(Contract)
                       .filter(Contract.contractTypeId == ContractType.id)
                       .filter(ContractType.contractType == 'race services')
                       .filter(Contract.templateTypeId == TemplateType.id)
                       .filter(TemplateType.templateType == 'late renewed reminder email')
                       .one()
                       ).block
        template = Template(templatestr)

        # bring in needed relations
        garbage = event.client

        # merge database fields into template and send email
        # deepcopy getting error AttributeError: 'Race' object has no attribute '_sa_instance_state'
        # so just collect what we need
        mergefields = deepcopy(event.__dict__)

        mergefields['event'] = event.race.race
        mergefields['renew_date'] = event.date

        html = template.render(mergefields)

        subject = 'Frederick Steeplechasers Services Reminder for {}'.format(event.race.race)
        tolist = event.client.contactEmail
        cclist = current_app.config['CONTRACTS_CC']
        fromlist = current_app.config['CONTRACTS_CONTACT']

        sendmail(subject, fromlist, tolist, html, ccaddr=cclist)

        # mark as sent
        event.tags.append(senttag)

        # pick up all db changes (event.tags)
        db.session.commit()

@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def cancellaterace(startdate, enddate):
    '''Cancel races for which we haven't heard back from client'''
    # set up tags which are used to control this email
    senttag = Tag.query.filter_by(tag=TAG_PRERACERENEWEDCANCELED).one()

    # calculate start and end date window
    if startdate == 'auto' and enddate == 'auto':
        # only send for races within one week window
        # this causes sending DAYS_PRERACE_LATE_CANCEL in advance of the event,
        # but if it doesn't happen for some reason will retry for a week
        start = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_PRERACE_LATE_CANCEL']) - timedelta(7))
        end = dbdate.dt2asc(date.today() + timedelta(current_app.config['DAYS_PRERACE_LATE_CANCEL']))

    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate == 'auto' or enddate == 'auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
                not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # debug
    if debug: print('start={} end={}'.format(start, end))

    # use filter to get races in which occurred at least N days ago
    events = Event.query.filter(Event.date.between(start, end)).all()

    for event in events:
        # ignore events unless they're in renewed-pending state
        if event.state.state != STATE_RENEWED_PENDING: continue

        # don't send email if this message has already been sent or was inhibited by admin
        # this is done for all events, regardless of what services were 'renewed'
        if senttag in event.tags: continue

        # cancel event
        event.state = State.query.filter_by(state=STATE_CANCELED).one()

        # get canceled email template
        templatestr = (db.session.query(Contract)
                       .filter(Contract.contractTypeId == ContractType.id)
                       .filter(ContractType.contractType == 'race services')
                       .filter(Contract.templateTypeId == TemplateType.id)
                       .filter(TemplateType.templateType == 'canceled email')
                       .one()
                       ).block
        template = Template(templatestr)

        # bring in needed relations
        garbage = event.client

        # merge database fields into template and send email
        # deepcopy getting error AttributeError: 'Race' object has no attribute '_sa_instance_state'
        # so just collect what we need
        mergefields = deepcopy(event.__dict__)

        mergefields['event'] = event.race.race
        mergefields['renew_date'] = event.date

        html = template.render(mergefields)

        subject = 'Automatically canceling {}'.format(event.race.race)
        tolist = current_app.config['CONTRACTS_CC']
        cclist = None
        fromlist = current_app.config['CONTRACTS_CONTACT']

        sendmail(subject, fromlist, tolist, html, ccaddr=cclist)

        # mark as sent
        event.tags.append(senttag)

        # pick up all db changes (event.tags)
        db.session.commit()

@contract.command()
@argument('startdate', default='auto')
@argument('enddate', default='auto')
@with_appcontext
@catch_errors
def renewsponsorship(startdate, enddate):
    '''Renew sponsorships for races within date window'''

    # calculate start and end date window
    if startdate == 'auto' and enddate == 'auto':
        # only send for races within one week window
        # this causes sending DAYS_PRERACE_PREMPROMO_EMAIL after race,
        # but if it doesn't happen for some reason will retry for a week
        # calculate start and end date window (try to send for 1 week)
        start = dbdate.dt2asc(date.today() - timedelta(current_app.config['DAYS_POSTRACE_RENEWSPONSORSHIP'] + 7))
        end = dbdate.dt2asc(date.today() - timedelta(current_app.config['DAYS_POSTRACE_RENEWSPONSORSHIP']))

    # verify both dates are present, check user input format is yyyy-mm-dd
    else:
        if startdate == 'auto' or enddate == 'auto':
            print('ERROR: startdate and enddate must both be specified')
            return

        if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate) or
                not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
            print('ERROR: startdate and enddate must be in yyyy-mm-dd format')
            return

        # cli specified dates format is fine, and both dates specified
        start = startdate
        end = enddate

    # use filter to get sponsorships for races in which occurred at least N days ago
    racedates = SponsorRaceDate.query.filter(SponsorRaceDate.racedate.between(start, end)).all()
    queries = []
    for racedate in racedates:
        queries.append({'race_id' : racedate.race_id, 'raceyear' : racedate.raceyear})

    sponsorships = []
    for query in queries:
        sponsorships += Sponsor.query.filter_by(**query).all()

    for sponsorship in sponsorships:
        # ignore uncommitted events
        if sponsorship.state.state != STATE_COMMITTED: continue

        # renew event
        newsponsorships = renew_sponsorship(sponsorship)

        # pick up any db changes related to renewal (renew, daterule, event.tags)
        db.session.commit()


#######################################################################
### the following commands are designed for initial deployment
#######################################################################

@contract.command()
@argument('startdate')
@argument('enddate')
@with_appcontext
@catch_errors
def xrenewraces(startdate, enddate):
    '''(initial deployment) Renew races between two dates yyyy-mm-dd'''

    # check input argument format
    if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate)
            or not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
        print('ERROR: dates must be in yyyy-mm-dd format')
        return

    # do arguments make sense?
    if enddate < startdate:
        print('ERROR: enddate must be greater than or equal to startdate')
        return

    # use filter to get races specified
    events = Event.query.filter(Event.date.between(startdate, enddate)).all()

    # keep track of events which were renewed
    newevents = []

    for event in events:
        # ignore uncommitted events
        if event.state.state != STATE_COMMITTED: continue

        # renew event
        newevent = renew_event(event)

        # may be marked as TAG_RACERENEWED, but no future event found, 
        # so protecting against that
        if newevent:
            # make sure race is brought in
            newevents.append(newevent)
        
        # pick up any db changes related to renewal (renew, daterule, event.tags)
        db.session.commit()

    if newevents:
        print('renewed events:')
        for newevent in newevents:
            print('   {} {}'.format(newevent.date, newevent.race.race))
    else:
        print('no events found')

@contract.command()
@argument('startdate')
@argument('enddate')
@with_appcontext
@catch_errors
def xsendrenewemails(startdate, enddate):
    '''(initial deployment) Send "renewal" emails for renewed events between two dates yyyy-mm-dd.
    NOTE: emails are not sent to premium promotion only events.
    '''

    # set up tag which is used to control this email
    senttag = Tag.query.filter_by(tag=TAG_POSTRACEMAILSENT).one()
    inhibittag = Tag.query.filter_by(tag=TAG_POSTRACEMAILINHIBITED).one()

    # check input argument format
    if (not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', startdate)
            or not match(r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$', enddate)):
        print('ERROR: dates must be in yyyy-mm-dd format')
        return

    # do arguments make sense?
    if enddate < startdate:
        print('ERROR: enddate must be greater than or equal to startdate')
        return

    # use filter to get races specified
    events = Event.query.filter(Event.date.between(startdate, enddate)).all()

    for event in events:
        # ignore events which are not renewed renewed
        if event.state.state != STATE_RENEWED_PENDING: continue

        # bring in event this was renewed from
        # the latest event associated with this race is the one, but before this one
        prevevents = Event.query.filter(Event.race_id == event.race_id).filter(Event.date < event.date).order_by(Event.date).all()
        prevevent = prevevents[-1]

        # don't send email if this message has already been sent or was inhibited by admin
        # don't send email if only premium promotion service
        if senttag in prevevent.tags or inhibittag in prevevent.tags: continue
        if len(event.services) == 1 and event.services[0].service == 'premiumpromotion': continue

        # get post-race mail template
        templatestr = (db.session.query(Contract)
                   .filter(Contract.contractTypeId==ContractType.id)
                   .filter(ContractType.contractType=='race services')
                   .filter(Contract.templateTypeId==TemplateType.id)
                   .filter(TemplateType.templateType=='post-race email')
                   .one()
                  ).block
        template = Template( templatestr )

        # bring in needed relations
        garbage = event.client
        garbage = event.lead
        garbage = event.course

        # merge database fields into template and send email
        # deepcopy getting error AttributeError: 'Race' object has no attribute '_sa_instance_state'
        # so just collect what we need
        mergefields = deepcopy(event.__dict__)

        mergefields['nextyeartext'] = 'based on your most recent race'
        mergefields['servicenames'] = [s.service for s in event.services] 
        mergefields['event'] = event.race.race
        # this shouldn't happen, but need to handle case where renew_event couldn't find renewed race
        mergefields['renew_date'] = event.date if event else '[oops - an error occurred determining race date, please contact us]'

        html = template.render( mergefields )

        subject = 'FSRC Race Support Services is holding {} for {}'.format(event.date, event.race.race)
        tolist = event.client.contactEmail
        cclist = current_app.config['CONTRACTS_CC']
        fromlist = current_app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        prevevent.tags.append(senttag)

        # pick up all db changes (event.tags)
        db.session.commit()

