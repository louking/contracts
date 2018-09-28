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
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.google import make_google_blueprint, google
from sqlalchemy.orm.exc import NoResultFound

# homegrown
from contracts.dbmodel import db, OAuth, User

#----------------------------------------------------
def init_login(app):
#----------------------------------------------------
    blueprint = make_google_blueprint(
        client_id   = app.config['GOOGLE_OAUTH_CLIENT_ID'],
        client_secret = app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
        scope=[
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/drive.file',
              ]
    )
    app.register_blueprint(blueprint, url_prefix="/login")

    # setup SQLAlchemy backend
    blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

    # create/login local user on successful OAuth login
    @oauth_authorized.connect_via(blueprint)
    def google_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with google.", category="error")
            return False

        resp = blueprint.session.get("/oauth2/v2/userinfo")
        if not resp.ok:
            msg = "Failed to fetch user info from google."
            flash(msg, category="error")
            return False

        google_info = resp.json()
        google_user_id = str(google_info["id"])

        # Find this OAuth token in the database, or create it
        query = OAuth.query.filter_by(
            provider=blueprint.name,
            provider_user_id=google_user_id,
        )
        try:
            oauth = query.one()
        except NoResultFound:
            oauth = OAuth(
                provider=blueprint.name,
                provider_user_id=google_user_id,
                token=token,
            )

        if oauth.user:
            # If this OAuth token already has an associated local account,
            # log in that local user account.
            # Note that if we just created this OAuth token, then it can't
            # have an associated local account yet.
            login_user(oauth.user)
            db.session.commit()

        else:
            # If this OAuth token doesn't have an associated local account,
            # verify local user account for this user exists. We can log
            # in that account as well, while we're at it.
            user = User.query.filter_by(email=google_info['email']).first()

            # if user exists, log them in
            if user:
                oauth.user = user

                # Save and commit our database models
                db.session.add_all([oauth])

                # Log in the new local user account
                login_user(user)
                db.session.commit()

            else:
                flash("Your email {} was not found. If you this this is in error, please contact raceservices@steeplechasers.org", 'error')

        # Since we're manually creating the OAuth model in the database,
        # we should return False so that Flask-Dance knows that
        # it doesn't have to do it. If we don't return False, the OAuth token
        # could be saved twice, or Flask-Dance could throw an error when
        # trying to incorrectly save it for us.
        return False

from . import bp
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    db.session.commit()
    flash("you've been logged out")
    return redirect(url_for("frontend.index"))