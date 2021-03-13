###########################################################################################
# contracts - package
#
#       Date            Author          Reason
#       ----            ------          ------
#       06/27/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###########################################################################################

# standard
import os.path

# pypi
from flask import Flask, send_from_directory
from jinja2 import ChoiceLoader, PackageLoader
from flask_security import Security, SQLAlchemyUserDatastore

# homegrown
import loutilities
from loutilities.configparser import getitems

# bring in js, css assets
from . import assets
from .assets import asset_env, asset_bundles

# get configuration
# configfile = "contracts.cfg"
# configpath = os.path.join(os.path.sep.join(os.path.dirname(__file__).split(os.path.sep)[:-1]), configfile)
# appconfig = getitems(configpath, 'app')
# app.config.update(appconfig)

# define security globals
user_datastore = None
security = None

# create application
def create_app(config_obj, configfiles=None, local_update=True):
    '''
    apply configuration object, then configuration filename
    '''
    global app
    app = Flask('contracts')
    app.config.from_object(config_obj)
    if configfiles:
        # backwards compatibility
        if type(configfiles) == str:
            configfiles = [configfiles]
        for configfile in configfiles:
            appconfig = getitems(configfile, 'app')
            app.config.update(appconfig)

    # tell jinja to remove linebreaks
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # define product name (don't import nav until after app.jinja_env.globals['_productname'] set)
    app.jinja_env.globals['_productname'] = app.config['THISAPP_PRODUCTNAME']
    app.jinja_env.globals['_productname_text'] = app.config['THISAPP_PRODUCTNAME_TEXT']

    # initialize database
    from contracts.dbmodel import db
    db.init_app(app)

    # add loutilities tables-assets for js/css/template loading
    # see https://adambard.com/blog/fresh-flask-setup/
    #    and https://webassets.readthedocs.io/en/latest/environment.html#webassets.env.Environment.load_path
    # loutilities.__file__ is __init__.py file inside loutilities; os.path.split gets package directory
    loutilitiespath = os.path.join(os.path.split(loutilities.__file__)[0], 'tables-assets', 'static')

    @app.route('/loutilities/static/<path:filename>')
    def loutilities_static(filename):
        return send_from_directory(loutilitiespath, filename)

    # bring in js, css assets here, because app needs to be created first
    from .assets import asset_env, asset_bundles
    with app.app_context():
        # uncomment when working on #346
        # # needs to be set before update_local_tables called and before UserSecurity() instantiated
        # g.loutility = Application.query.filter_by(application=app.config['APP_LOUTILITY']).one()
        #
        # # update LocalUser and LocalInterest tables
        # if local_update:
        #     update_local_tables()

        # js/css files
        asset_env.append_path(app.static_folder)
        asset_env.append_path(loutilitiespath, '/loutilities/static')

        # templates
        loader = ChoiceLoader([
            app.jinja_loader,
            PackageLoader('loutilities', 'tables-assets/templates')
        ])
        app.jinja_loader = loader

    # initialize assets
    asset_env.init_app(app)
    asset_env.register(asset_bundles)

    # Set up Flask-Security
    from contracts.dbmodel import User, Role
    global user_datastore, security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # activate views
    from contracts.views.frontend import bp as frontend
    app.register_blueprint(frontend)

    # need to force app context else get
    #    RuntimeError: Working outside of application context.
    #    RuntimeError: Attempted to generate a URL without the application context being pushed.
    # see http://kronosapiens.github.io/blog/2014/08/14/understanding-contexts-in-flask.html
    with app.app_context():
        # admin views need to be defined within app context because of requests.addscripts() using url_for
        from contracts.views.admin import bp as admin
        app.register_blueprint(admin)

        # import navigation after views created
        from . import nav

        # turn on logging
        from .applogging import setlogging
        setlogging()

        # set up scoped session
        from sqlalchemy.orm import scoped_session, sessionmaker
        db.session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=db.engine))
        db.query = db.session.query_property()

    # app back to caller
    return app

# set static, templates if configured
# app.static_folder = appconfig.get('STATIC_FOLDER', 'static')
# app.template_folder = appconfig.get('TEMPLATE_FOLDER', 'templates')

# # configure for debug
# debug = app.config['DEBUG']
# if debug:
#     app.config['SECRET_KEY'] = 'flask development key'





