"""system information and debug views

Raises:
    testException: test exception handling
"""

# standard

# pypi
from flask import current_app, make_response, request, render_template, session
from flask.views import MethodView
from flask_security import roles_accepted
from loutilities.flask_helpers.blueprints import add_url_rules

# home grown
from . import bp
from ...dbmodel import db 
from ...version import __version__
from ...version import __docversion__

adminguide = f'https://contractility.readthedocs.io/en/{__docversion__}/contract-admin-guide.html'

class testException(Exception): pass

thisversion = __version__

class ViewSysinfo(MethodView):
    url_rules = {
                'sysinfo': ['/sysinfo',('GET',)],
                }

    def get(self):
        try:
            # commit database updates and close transaction
            db.session.commit()
            return render_template('sysinfo.jinja2', pagename='About', adminguide=adminguide, version=thisversion)
        
        except:
            # roll back database updates and close transaction
            db.session.rollback()
            raise
add_url_rules(bp, ViewSysinfo)

class ViewDebug(MethodView):
    decorators = [lambda f: roles_accepted('super-admin')(f)]
    url_rules = {
                'debug': ['/_debuginfo',('GET',)],
                }
    def get(self):
        try:
            appconfigpath = getattr(current_app,'configpath','<not set>')
            appconfigtime = getattr(current_app,'configtime','<not set>')

            # collect groups of system variables                        
            sysvars = []
            
            # collect current_app.config variables
            configkeys = sorted(list(current_app.config.keys()))
            appconfig = []
            for key in configkeys:
                value = current_app.config[key]
                if True:    # maybe check for something else later
                    if key in ['SQLALCHEMY_BINDS''SQLALCHEMY_DATABASE_URI', 'SECRET_KEY', 'GOOGLE_OAUTH_CLIENT_ID', 
                               'GOOGLE_OAUTH_CLIENT_SECRET', 'MAIL_PASSWORD', 'RSU_KEY', 'RSU_SECRET', 'PASSWORD_SALT']:
                        value = '<obscured>'
                appconfig.append({'label':key, 'value':value})
            sysvars.append(['current_app.config',appconfig])
            
            # collect flask.session variables
            sessionkeys = sorted(session.keys())
            sessionconfig = []
            for key in sessionkeys:
                value = session[key]
                sessionconfig.append({'label':key, 'value':value})
            sysvars.append(['flask.session',sessionconfig])
            
            # commit database updates and close transaction
            db.session.commit()
            return render_template('sysinfo.jinja2',pagename='Debug',
                                         version=thisversion,
                                         configpath=appconfigpath,
                                         configtime=appconfigtime,
                                         adminguide=adminguide,
                                         sysvars=sysvars,
                                         inhibityear=True,inhibitclub=True)
        
        except:
            # roll back database updates and close transaction
            db.session.rollback()
            raise
add_url_rules(bp, ViewDebug)


class TestException(MethodView):
    decorators = [lambda f: roles_accepted('super-admin')(f)]
    url_rules = {
                'testexception': ['/xcauseexception',('GET',)],
                }
    def get(self):
        try:
            raise testException
                    
        except:
            # roll back database updates and close transaction
            db.session.rollback()
            raise
add_url_rules(bp, TestException)
