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

# homegrown
from contracts.dbmodel import db, User
from loutilities.googleauth import GoogleAuth, get_credentials

# needful constants
APP_CRED_FOLDER = current_app.config['APP_CRED_FOLDER']

#----------------------------------------------------------------------
def do_login(email):
#----------------------------------------------------------------------
    # verify local user account for this user exists. We can log
    # in that account as well, while we're at it.
    user = User.query.filter_by(email=email).first()

    # if user exists, log them in
    if user:
        # Log in the new local user account
        login_user(user)
        db.session.commit()

    else:
        flash("Your email {} was not found. If you this this is in error, please contact raceservices@steeplechasers.org".format(email), 'error')
        do_logout()
        googleauth.clear_credentials()

#----------------------------------------------------------------------
def do_logout():
#----------------------------------------------------------------------
    logout_user()
    db.session.commit()

#############################################
# google auth views
appscopes = [ 'https://www.googleapis.com/auth/plus.me',
              'https://www.googleapis.com/auth/userinfo.email',
              'https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/drive.file' ]
googleauth = GoogleAuth(current_app, current_app.config['APP_CLIENT_SECRETS_FILE'], appscopes, 'frontend.index', 
                        credfolder=APP_CRED_FOLDER, 
                        logincallback=do_login, logoutcallback=do_logout,
                        loginfo=current_app.logger.info, logdebug=current_app.logger.debug, logerror=current_app.logger.error)

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
        googleauth.clear_credentials()
        return redirect(url_for('frontend.index'))

#############################################
# logout handling
logout = Logout(current_app)
