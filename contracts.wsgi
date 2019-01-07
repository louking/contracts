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
from ConfigParser import SafeConfigParser

# debug - information about python environment
# goes to /var/log/httpd/error_log, per http://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html
if True:
    import platform
    print >> sys.stderr, 'started with python {}, {}'.format(platform.python_version(), platform.python_compiler())


# set configuration file, for here and for app
os.environ['RSC_CONFIG_FILE'] = 'contracts.cfg'

# get configuration
config = SafeConfigParser()
thisdir = os.path.dirname(__file__)
configpath = os.path.join(os.path.dirname(thisdir), 'config', os.environ['RSC_CONFIG_FILE'])
config.readfp(open(os.path.join(configpath, os.environ['RSC_CONFIG_FILE'])))
PROJECT_DIR = config.get('project', 'PROJECT_DIR')
# remove quotes if present
if PROJECT_DIR[0] == '"': PROJECT_DIR = PROJECT_DIR[1:-1]

# activate virtualenv
activate_this = os.path.join(PROJECT_DIR, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.append(PROJECT_DIR)
sys.path.append(thisdir)

# debug - which user is starting this?
# goes to /var/log/httpd/error_log, per http://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html
if False:
    from getpass import getuser
    print >> sys.stderr, 'contracts user = {}'.format(getuser())

from contracts import app as application
