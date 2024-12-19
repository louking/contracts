###########################################################################################
# frontend - views for contracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       06/29/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
frontend - views for contracts database
=======================================================================
'''

# pypi
from flask import render_template
from flask.views import MethodView
from loutilities.flask_helpers.blueprints import add_url_rules

# home grown
from . import bp
from ...version import __docversion__

adminguide = f'https://contractility.readthedocs.io/en/{__docversion__}/contract-admin-guide.html'

#######################################################################
class Index(MethodView):
#######################################################################
    url_rules = {
                'index': ['/',('GET',)],
                }

    def get(self):
        return render_template('index.jinja2', adminguide=adminguide)

#----------------------------------------------------------------------
add_url_rules(bp, Index)
#----------------------------------------------------------------------
