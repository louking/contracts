###########################################################################################
# test_basic - test root page
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/14/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################

# contracts/test_basic.py
 
import pytest

def create_user(email, roles):
    from contracts import user_datastore
    from contracts.dbmodel import db
    user = user_datastore.create_user(email=email)
    if type(roles) != list:
        roles = [roles]
    for role in roles:
        user_datastore.add_role_to_user(user, role)
    db.session.commit()

def login_test_user(email):
    from contracts.dbmodel import db, User
    from flask_security import login_user
    user = User.query.filter_by(email=email).one()
    login_user(user)
    db.session.commit()

# def test_main_page(app):
#     resp = app.test_client().get('/', follow_redirects=True)
#     assert resp.status_code == 200
#     assert 'title="Home"' in resp.data
 
def test_login(dbapp):
    app = dbapp
    from contracts.dbmodel import db, init_db
    from contracts import user_datastore
    from flask import url_for
    # init_db should create at least superadmin, admin roles
    init_db(defineowner=False)
    useremail = 'testuser@example.com'
    with app.test_client() as client:
        create_user(useremail, 'superadmin')
        login_test_user(useremail)
        resp = client.get('/', follow_redirects=True)
        assert resp.status_code == 200
        assert url_for('admin.logout') in resp.data



