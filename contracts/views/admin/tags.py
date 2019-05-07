###########################################################################################
# tags - manage tags
#
#       Date            Author          Reason
#       ----            ------          ------
#       12/20/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
tags - manage tags
====================================================
'''

# homegrown
from . import bp
from contracts.dbmodel import db, Tag, SponsorTag
from contracts.crudapi import DbCrudApiRolePermissions

###########################################################################################
# tags endpoint
###########################################################################################

tag_dbattrs = 'id,tag,description,isBuiltIn'.split(',')
tag_formfields = 'rowid,tag,description,isBuiltIn'.split(',')
tag_dbmapping = dict(zip(tag_dbattrs, tag_formfields))
tag_formmapping = dict(zip(tag_formfields, tag_dbattrs))

tag = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Tag, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'tags', 
                    endpoint = 'admin.tags', 
                    rule = '/tags', 
                    dbmapping = tag_dbmapping, 
                    formmapping = tag_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'tag', 'name': 'tag', 'label': 'Tag', '_unique': True, 
                          'className': 'field_req',
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description', 
                          'className': 'field_req',
                        },
                        { 'data': 'isBuiltIn', 'name': 'isBuiltIn', 'label': 'Built In',
                          'ed':{ 'def': 'no', 'type':'hidden' }, 
                          '_treatment' : { 'boolean' : { 'formfield':'isBuiltIn', 'dbfield':'isBuiltIn' } }
                        },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    # TODO: no edit now due to #123, but logic could be added to edit tags which have isBuiltIn==False
                    buttons = ['create', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                  },
                    )
tag.register()

###########################################################################################
# super_tags endpoint (only for super-admins)
###########################################################################################

super_tag_dbattrs = 'id,tag,description,isBuiltIn'.split(',')
super_tag_formfields = 'rowid,tag,description,isBuiltIn'.split(',')
super_tag_dbmapping = dict(zip(super_tag_dbattrs, super_tag_formfields))
super_tag_formmapping = dict(zip(super_tag_formfields, super_tag_dbattrs))

super_tag = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Tag, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'super tags', 
                    endpoint = 'admin.super-tags', 
                    rule = '/super-tags', 
                    dbmapping = super_tag_dbmapping, 
                    formmapping = super_tag_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'tag', 'name': 'tag', 'label': 'Tag', '_unique': True, 
                          'className': 'field_req',
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description', 
                          'className': 'field_req',
                        },
                        { 'data': 'isBuiltIn', 'name': 'isBuiltIn', 'label': 'Built In',
                          'ed':{ 'def': 'no' }, 
                          '_treatment' : { 'boolean' : { 'formfield':'isBuiltIn', 'dbfield':'isBuiltIn' } }
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
super_tag.register()

###########################################################################################
# sponsortags endpoint
###########################################################################################

sponsortag_dbattrs = 'id,tag,description,isBuiltIn'.split(',')
sponsortag_formfields = 'rowid,tag,description,isBuiltIn'.split(',')
sponsortag_dbmapping = dict(zip(sponsortag_dbattrs, sponsortag_formfields))
sponsortag_formmapping = dict(zip(sponsortag_formfields, sponsortag_dbattrs))

sponsortag = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorTag,
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'sponsir-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Sponsorship Tags',
                    endpoint = 'admin.sponsortags', 
                    rule = '/sponsorshiptags',
                    dbmapping = sponsortag_dbmapping, 
                    formmapping = sponsortag_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'tag', 'name': 'tag', 'label': 'Tag', '_unique': True,
                          'className': 'field_req',
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description', 
                          'className': 'field_req',
                        },
                        { 'data': 'isBuiltIn', 'name': 'isBuiltIn', 'label': 'Built In',
                          'ed':{ 'def': 'no', 'type':'hidden' }, 
                          '_treatment' : { 'boolean' : { 'formfield':'isBuiltIn', 'dbfield':'isBuiltIn' } }
                        },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    # TODO: no edit now due to #123, but logic could be added to edit sponsortags which have isBuiltIn==False
                    buttons = ['create', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                  },
                    )
sponsortag.register()

###########################################################################################
# super_sponsortags endpoint (only for super-admins)
###########################################################################################

super_sponsortag_dbattrs = 'id,tag,description,isBuiltIn'.split(',')
super_sponsortag_formfields = 'rowid,tag,description,isBuiltIn'.split(',')
super_sponsortag_dbmapping = dict(zip(super_sponsortag_dbattrs, super_sponsortag_formfields))
super_sponsortag_formmapping = dict(zip(super_sponsortag_formfields, super_sponsortag_dbattrs))

super_sponsortag = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorTag,
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'super sponsorship tags',
                    endpoint = 'admin.super-sponsortags', 
                    rule = '/super-sponsorshiptags',
                    dbmapping = super_sponsortag_dbmapping, 
                    formmapping = super_sponsortag_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'tag', 'name': 'tag', 'label': 'Tag', '_unique': True,
                          'className': 'field_req',
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description', 
                          'className': 'field_req',
                        },
                        { 'data': 'isBuiltIn', 'name': 'isBuiltIn', 'label': 'Built In',
                          'ed':{ 'def': 'no' }, 
                          '_treatment' : { 'boolean' : { 'formfield':'isBuiltIn', 'dbfield':'isBuiltIn' } }
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
super_sponsortag.register()

