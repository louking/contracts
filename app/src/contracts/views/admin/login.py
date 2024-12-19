###########################################################################################
# login - log in/out from administrative console
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/06/18        Lou King        Create
#
#   Copyright 2018 Lou King
###########################################################################################

'''
login - log in / out from admin console
==========================================
'''

# pypi
from flask import flash, session, current_app, redirect, url_for
from flask_security import current_user, login_user, login_required, logout_user
from flask.views import View
from loutilities.user.model import User

# homegrown
from contracts.dbmodel import db
from loutilities.googleauth import GoogleAuth, get_credentials, get_email

#######################################################################
class Logout(View):
#######################################################################

    #----------------------------------------------------------------------
    def __init__( self, app ):
    #----------------------------------------------------------------------
        self.app = app
        self.app.add_url_rule('/admin/logout', view_func=self.logout, methods=['GET',])

    #----------------------------------------------------------------------
    def logout( self ):
    #----------------------------------------------------------------------
        return redirect(url_for('frontend.index'))

#############################################
# logout handling
logout = Logout(current_app)
