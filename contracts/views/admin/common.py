###########################################################################################
# common - views and apis common to different admin types
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/09/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
common - views and apis common to different admin types
==========================================================
'''

# standard
from re import match

# pypi
from flask_security import roles_accepted, current_user

# homegrown
from . import bp
from contracts.dbmodel import db, Client, State
from contracts.crudapi import DbCrudApiRolePermissions
from contracts.crudapi import REGEX_URL, REGEX_EMAIL

##########################################################################################
# clients endpoint
###########################################################################################

client_dbattrs = 'id,client,clientUrl,contactFirstName,contactLastName,contactEmail,contactTitle,clientPhone,clientAddr,notes'.split(',')
client_formfields = 'rowid,client,clientUrl,contactFirstName,contactLastName,contactEmail,contactTitle,clientPhone,clientAddr,notes'.split(',')
client_dbmapping = dict(list(zip(client_dbattrs, client_formfields)))
client_formmapping = dict(list(zip(client_formfields, client_dbattrs)))

def client_validate(action, formdata):
    results = []

    # regex patterns from http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
    for field in ['clientUrl']:
        if formdata[field] and not match(REGEX_URL, formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid url: correct format is like http[s]://example.com' })

    for field in ['contactEmail']:
        if formdata[field] and not match(REGEX_EMAIL, formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid email: correct format is like john.doe@example.com' })

    return results

client = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Client, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    pagename = 'clients', 
                    roles_accepted = ['event-admin', 'sponsor-admin', 'super-admin'],
                    template = 'datatables.jinja2',
                    endpoint = 'admin.clients-admin', 
                    rule = '/clients', 
                    dbmapping = client_dbmapping, 
                    formmapping = client_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'client', 'name': 'client', 'label': 'Client Name', '_unique':True,
                          'className': 'field_req',
                        },
                        { 'data': 'clientUrl', 'name': 'clientUrl', 'label': 'Client URL' },
                        { 'data': 'contactFirstName', 'name': 'contactFirstName', 'label': 'Contact First Name',
                          'className': 'field_req',
                        },
                        { 'data': 'contactLastName', 'name': 'contactLastName', 'label': 'Contact Last Name',
                          'className': 'field_req',
                        },
                        { 'data': 'contactEmail', 'name': 'contactEmail', 'label': 'Contact Email',
                          'className': 'field_req',
                        },
                        { 'data': 'contactTitle', 'name': 'contactTitle', 'label': 'Contact Title',
                        },
                        { 'data': 'clientPhone', 'name': 'clientPhone', 'label': 'Client Phone' },
                        { 'data': 'clientAddr', 'name': 'clientAddr', 'label': 'Client Address', 'type': 'textarea' },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type': 'textarea' },
                    ], 
                    validate = client_validate,
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'editRefresh', 'remove'],
                    dtoptions = {
                                'scrollCollapse': True,
                                'scrollX': True,
                                'scrollXInner': "100%",
                                'scrollY': True,
                                'lengthMenu': [ [-1, 10, 25, 50], ["All", 10, 25, 50] ],
                                },
                    )
client.register()

##########################################################################################
# states endpoint
###########################################################################################

state_dbattrs = 'id,state,description'.split(',')
state_formfields = 'rowid,state,description'.split(',')
state_dbmapping = dict(list(zip(state_dbattrs, state_formfields)))
state_formmapping = dict(list(zip(state_formfields, state_dbattrs)))

state = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = State, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'states', 
                    endpoint = 'admin.states', 
                    rule = '/states', 
                    dbmapping = state_dbmapping, 
                    formmapping = state_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'state', 'name': 'state', 'label': 'State', 
                          'className': 'field_req',
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description', 
                          'className': 'field_req',
                        },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'editRefresh', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                  },
                    )
state.register()

