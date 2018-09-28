###########################################################################################
# userroles - manage application users and roles
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/09/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
userroles - manage application users and roles
====================================================
'''

# standard

# pypi
from flask_security import roles_accepted, current_user

# homegrown
from . import bp
from racesupportcontracts.dbmodel import db, User, Role
from racesupportcontracts.crudapi import DbCrudApiRolePermissions
from racesupportcontracts.request import addscripts

##########################################################################################
# users endpoint
###########################################################################################

user_dbattrs = 'id,email,name,given_name,roles,last_login_at,current_login_at,last_login_ip,current_login_ip,login_count,active'.split(',')
user_formfields = 'rowid,email,name,given_name,roles,last_login_at,current_login_at,last_login_ip,current_login_ip,login_count,active'.split(',')
user_dbmapping = dict(zip(user_dbattrs, user_formfields))
user_formmapping = dict(zip(user_formfields, user_dbattrs))

user = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = User, 
                    roles_accepted = 'superadmin',
                    template = 'datatables.jinja2',
                    pagename = 'users', 
                    endpoint = 'admin.users', 
                    rule = '/users', 
                    dbmapping = user_dbmapping, 
                    formmapping = user_formmapping, 
                    clientcolumns = [
                        { 'data': 'email', 'name': 'email', 'label': 'Email' },
                        { 'data': 'name', 'name': 'name', 'label': 'Full Name' },
                        { 'data': 'given_name', 'name': 'given_name', 'label': 'First Name' },
                        { 'data': 'roles', 'name': 'roles', 'label': 'Roles', 
                          '_treatment' : { 'relationship' : { 'model':Role, 'modelfield':'name', 'formfield':'roles', 'dbfield':'roles', 'uselist':True } }
                        },
                        { 'data': 'active', 'name': 'active', 'label': 'Active', 
                          '_treatment' : { 'boolean' : { 'formfield':'active', 'dbfield':'active' } },
                        },
                        { 'data': 'last_login_at', 'name': 'last_login_at', 'label': 'Last Login At', 'type': 'readonly' },
                        { 'data': 'current_login_at', 'name': 'current_login_at', 'label': 'Current Login At', 'type': 'readonly' },
                        { 'data': 'last_login_ip', 'name': 'last_login_ip', 'label': 'Last Login IP', 'type': 'readonly' },
                        { 'data': 'current_login_ip', 'name': 'current_login_ip', 'label': 'Current Login IP', 'type': 'readonly' },
                        { 'data': 'login_count', 'name': 'login_count', 'label': 'Login Count', 'type': 'readonly' },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'edit', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                  },
                        scriptfilter = addscripts,
                    )
user.register()

##########################################################################################
# roles endpoint
###########################################################################################

role_dbattrs = 'id,name,description'.split(',')
role_formfields = 'rowid,name,description'.split(',')
role_dbmapping = dict(zip(role_dbattrs, role_formfields))
role_formmapping = dict(zip(role_formfields, role_dbattrs))

role = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Role, 
                    roles_accepted = 'superadmin',
                    template = 'datatables.jinja2',
                    pagename = 'roles', 
                    endpoint = 'admin.roles', 
                    rule = '/roles', 
                    dbmapping = role_dbmapping, 
                    formmapping = role_formmapping, 
                    clientcolumns = [
                        { 'data': 'name', 'name': 'name', 'label': 'Name' },
                        { 'data': 'description', 'name': 'description', 'label': 'Description' },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'edit', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                  },
                        scriptfilter = addscripts,
                    )
role.register()

