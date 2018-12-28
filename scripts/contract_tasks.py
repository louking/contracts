###########################################################################################
# event_tasks - background tasks needed for contract event management
#
#       Date            Author          Reason
#       ----            ------          ------
#       12/20/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
event_tasks - background tasks needed for contract event management
=======================================================================

'''
# standard
import os
import os.path
from copy import deepcopy
from datetime import date, timedelta
from urllib import quote_plus

# pypi
from flask import Flask
from sqlalchemy.orm import scoped_session, sessionmaker
from jinja2 import Template

# homegrown
from contracts.dbmodel import db, Event, Contract, ContractType, TemplateType, Tag
from contracts.dbmodel import TAG_PRERACEMAILSENT, TAG_PRERACEMAILINHIBITED
from contracts.dbmodel import TAG_POSTRACEMAILSENT, TAG_POSTRACEMAILINHIBITED, TAG_RACERENEWED
from contracts.dbmodel import STATE_COMMITTED
from contracts.settings import Production
from contracts.mailer import sendmail
from contracts.utils import renew_event
from contracts.applogging import setlogging
from loutilities.configparser import getitems
from loutilities.timeu import asctime

# create app and get configuration
app = Flask(__name__)
dirname = os.path.dirname(__file__)
# one level up
dirname = os.path.dirname(dirname)
configdir = os.path.join(dirname, 'config')
configfile = "contracts.cfg"
configpath = os.path.join(configdir, configfile)
app.config.from_object(Production(configpath))
appconfig = getitems(configpath, 'app')
app.config.update(appconfig)

# set up database
db.init_app(app)

# set up scoped session
with app.app_context():
    db.session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=db.engine))
    db.query = db.session.query_property()

    # turn on logging
    setlogging()

# set up datatabase date formatter
dbdate = asctime('%Y-%m-%d')

#----------------------------------------------------------------------
@app.cli.command()
def hello():
#----------------------------------------------------------------------
    print 'hello world'

#----------------------------------------------------------------------
@app.cli.command()
def preraceemail():
#----------------------------------------------------------------------
    # set up tag which is used to control this email
    senttag = Tag.query.filter_by(tag=TAG_PRERACEMAILSENT).one()
    inhibittag = Tag.query.filter_by(tag=TAG_PRERACEMAILINHIBITED).one()

    # calculate start and end date window
    start = dbdate.dt2asc(date.today())
    end = dbdate.dt2asc(date.today() + timedelta(app.config['DAYS_PRERACE_EMAIL'] - 1))

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

        # merge database fields into template and send email
        mergefields = deepcopy(event.__dict__)
        docid = event.contractDocId

        mergefields['viewcontracturl'] = 'https://docs.google.com/document/d/{}/view'.format(docid)
        mergefields['servicenames'] = [s.service for s in event.services] 
        mergefields['event'] = event.race.race

        html = template.render( mergefields )

        subject = 'FSRC Pre-race Coordination: {} - {}'.format(event.race.race, event.date)
        tolist = event.client.contactEmail
        cclist = app.config['CONTRACTS_CC'] + [event.lead.email]
        fromlist = app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        event.tags.append(senttag)
        db.session.commit()

#----------------------------------------------------------------------
@app.cli.command()
def postraceprocessing():
#----------------------------------------------------------------------
    # set up tag which is used to control this email
    senttag = Tag.query.filter_by(tag=TAG_POSTRACEMAILSENT).one()
    inhibittag = Tag.query.filter_by(tag=TAG_POSTRACEMAILINHIBITED).one()

    # calculate start and end date window (try to send for 1 week)
    start = dbdate.dt2asc(date.today() - timedelta(app.config['DAYS_POSTRACE_EMAIL'] + 7) )
    end = dbdate.dt2asc(date.today() - timedelta(app.config['DAYS_POSTRACE_EMAIL'] ) )

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

        # merge database fields into template and send email
        # deepcopy getting error AttributeError: 'Race' object has no attribute '_sa_instance_state'
        # so just collect what we need
        # mergefields = deepcopy(event.__dict__)
        mergefields = {}
        docid = event.contractDocId

        mergefields['client'] = event.client
        mergefields['viewcontracturl'] = 'https://docs.google.com/document/d/{}/view'.format(docid)
        mergefields['servicenames'] = [s.service for s in event.services] 
        mergefields['event'] = event.race.race
        # this shouldn't happen, but need to handle case where renew_event couldn't find renewed race
        mergefields['renew_date'] = newevent.date if newevent else '[oops - an error occurred determining race date, please contact us]'

        surveyfields = {
            'eventencoded' : quote_plus(event.race.race),
            'dateencoded'  : quote_plus(event.date),
        }
        surveytemplate = Template( app.config['CONTRACTS_SURVEY_URL'] )
        mergefields['surveylink'] = surveytemplate.render( surveyfields )

        html = template.render( mergefields )

        subject = 'Thank You for using FSRC Race Support Services - {}'.format(event.date)
        tolist = event.client.contactEmail
        cclist = app.config['CONTRACTS_CC']
        fromlist = app.config['CONTRACTS_CONTACT']
        
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # mark as sent
        event.tags.append(senttag)

        # pick up all db changes (event.tags)
        db.session.commit()