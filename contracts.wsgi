###########################################################################################
# contracts.wsgi - run the web application
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/21/17        Lou King        Create
#
#   Copyright 2017 Lou King
###########################################################################################

import os, sys
from configparser import SafeConfigParser

# debug - information about python environment
# goes to /var/log/httpd/error_log, per http://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html
if True:
    import platform
    print('started with python {}, {}'.format(platform.python_version(), platform.python_compiler()), file=sys.stderr)


# set configuration file, for here and for app
os.environ['CONFIG_FILE'] = 'contracts.cfg'

# get configuration
config = SafeConfigParser()
thisdir = os.path.dirname(__file__)
configpath = os.path.join(os.path.dirname(thisdir), 'contracts', 'config', os.environ['CONFIG_FILE'])
config.readfp(open(os.path.join(configpath)))
PROJECT_DIR = config.get('project', 'PROJECT_DIR')
# remove quotes if present
if PROJECT_DIR[0] == '"': PROJECT_DIR = PROJECT_DIR[1:-1]

# activate virtualenv
activate_this = os.path.join(PROJECT_DIR, 'bin', 'activate_this.py')
exec(compile(open(activate_this, "rb").read(), activate_this, 'exec'), dict(__file__=activate_this))
sys.path.append(PROJECT_DIR)
sys.path.append(thisdir)

# debug - which user is starting this?
# goes to /var/log/httpd/error_log, per http://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html
if False:
    from getpass import getuser
    print('contracts user = {}'.format(getuser()), file=sys.stderr)

# from contracts import app as application
from contracts import create_app
from contracts.settings import Production
application = create_app(Production(configpath), configpath)

# see https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/#deploying-proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
application.wsgi_app = ProxyFix(application.wsgi_app, x_proto=1, x_host=1)
