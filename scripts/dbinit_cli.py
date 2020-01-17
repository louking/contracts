###########################################################################################
# dbinit_cli - command line database initialization
#
#       Date            Author          Reason
#       ----            ------          ------
#       12/20/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
dbinit_cli - command line database initialization
=======================================================================

'''
# standard
import os
import os.path
from copy import deepcopy
from datetime import date, timedelta
from urllib import quote_plus
from re import match

# pypi
from flask import Flask
from sqlalchemy.orm import scoped_session, sessionmaker
from flask.cli import AppGroup
from click import argument

# homegrown
from contracts.dbmodel import db, Sponsor
from contracts.settings import Production
from contracts.applogging import setlogging
from loutilities.configparser import getitems
from loutilities.timeu import asctime

class parameterError(Exception): pass

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

# start command group dbinit
dbinit_cli = AppGroup('dbinit', help='initialize database table groups')

#----------------------------------------------------------------------
@dbinit_cli.command('sponsortables')
def dbinit_sponsortables():
#----------------------------------------------------------------------
    '''
    initialize sponsor tables sponsorraces, sponsorlevels, sponsorbenefits
    '''
    with app.app_context():
        from contracts.dbinit_sponsors import dbinit_sponsors
        dbinit_sponsors()

#----------------------------------------------------------------------
@dbinit_cli.command('base')
def dbinit_basetables():
#----------------------------------------------------------------------
    '''
    initialize base tables state, course, service, etc
    '''
    with app.app_context():
        from contracts.dbinit_contracts import dbinit_base
        dbinit_base()

#----------------------------------------------------------------------
@dbinit_cli.command('tags')
def dbinit_tagtables():
#----------------------------------------------------------------------
    '''
    initialize tags table
    '''
    with app.app_context():
        from contracts.dbinit_contracts import dbinit_tags
        dbinit_tags()

#----------------------------------------------------------------------
@dbinit_cli.command('contracts')
def dbinit_contractstables():
#----------------------------------------------------------------------
    '''
    initialize contracts tables contract, template, contracttype, contractblocktype
    '''
    with app.app_context():
        from contracts.dbinit_contracts import dbinit_contracts
        dbinit_contracts()

#----------------------------------------------------------------------
@dbinit_cli.command('trends')
def dbinit_sponsortrends():
#----------------------------------------------------------------------
    '''
    initialize trends in sponsors table
    '''
    with app.app_context():
        from contracts.trends import calculateTrend
        for sponsorrec in Sponsor.query.all():
            calculateTrend(sponsorrec)
        db.session.commit()

# must be at end
app.cli.add_command(dbinit_cli)