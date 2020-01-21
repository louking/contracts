###########################################################################################
# dbinit - contracts database initialization
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/18/18        Lou King        Create
#
#   Copyright 2018 Lou King
###########################################################################################
'''
dbinit - contracts database initialization
==================================================
'''

# homegrown
from .dbmodel import db, Role, User

#--------------------------------------------------------------------------
def init_db(defineowner=True):
#--------------------------------------------------------------------------
    # init the modelitems from dbinit_contracts
    from .dbinit_contracts import dbinit_base, dbinit_tags, dbinit_contracts
    from .dbinit_sponsors import dbinit_sponsors
    dbinit_base()
    dbinit_tags()
    dbinit_contracts()
    dbinit_sponsors()

    # must wait until user_datastore is initialized before import
    from contracts import user_datastore

    # special processing for user roles because need to remember the roles when defining the owner
    # define user roles here
    userroles = [
        {'name':'super-admin',   'description':'everything'},
        {'name':'event-admin',   'description':'event administrator'},
        {'name':'sponsor-admin', 'description':'sponsorship administrator'},
        {'name':'notes',         'description':'can only edit notes'},
    ]

    # initialize roles, remembering what roles we have    
    allroles = {}
    for userrole in userroles:
        rolename = userrole['name']
        allroles[rolename] = Role.query.filter_by(name=rolename).first() or user_datastore.create_role(**userrole)
    
    # define owner if desired
    if defineowner:
        from flask import current_app
        rootuser = current_app.config['APP_OWNER']
        owner = User.query.filter_by(email=rootuser).first()
        if not owner:
            owner = user_datastore.create_user(email=rootuser)
            for rolename in allroles:
                user_datastore.add_role_to_user(owner, allroles[rolename])

    # and we're done, let's accept what we did
    db.session.commit()
