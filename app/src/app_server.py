'''
app.py is only used to support flask commands

app_server.py for webserver execution
    must match with app.py except for under "flask command processing"
'''
# standard
import os.path
from os import environ

# pypi

# homegrown
from contracts import create_app
from contracts.settings import Production

appname = environ['APP_NAME']

abspath = os.path.abspath('/config')
configpath = os.path.join(abspath, f'{appname}.cfg')
userconfigpath = os.path.join(abspath, 'users.cfg')
# userconfigpath first so configpath can override
configfiles = [userconfigpath, configpath]

# init_for_operation=True because we want operational behavior
# sqlalchemy.exc.OperationalError if one of the updating tables needs migration
app = create_app(Production(configfiles), configfiles, init_for_operation=True)

# Needed only if serving web pages
# implement proxy fix (https://github.com/sjmf/reverse-proxy-minimal-example)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_port=1, x_proto=1, x_prefix=1)


