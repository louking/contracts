'''
app.py is only used to support flask cli commands

develop execution from run.py; production execution from members.wsgi
'''
# standard
import os.path

# pypi
from flask_migrate import Migrate

# homegrown
from contracts import create_app
from contracts.settings import Production
from contracts.dbmodel import db
from contracts.applogging import setlogging

abspath = os.path.abspath(__file__)
configpath = os.path.join(os.path.dirname(abspath), 'config', 'contracts.cfg')

# userconfigpath first so configpath can override
userconfigpath = os.path.join(os.path.dirname(abspath), 'config', 'users.cfg')
configfiles = [userconfigpath, configpath]

# init_for_operation=False because when we create app this would use database and cause
# sqlalchemy.exc.OperationalError if one of the updating tables needs migration
app = create_app(Production(configfiles), configfiles, init_for_operation=False)

# set up scoped session
with app.app_context():
    # turn on logging
    setlogging()

migrate = Migrate(app, db, compare_type=True)


