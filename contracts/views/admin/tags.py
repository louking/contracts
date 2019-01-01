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
from contracts.dbmodel import db, Tag
from contracts.crudapi import DbCrudApiRolePermissions

###########################################################################################
# tags endpoint
###########################################################################################

tag_dbattrs = 'id,tag,description'.split(',')
tag_formfields = 'rowid,tag,description'.split(',')
tag_dbmapping = dict(zip(tag_dbattrs, tag_formfields))
tag_formmapping = dict(zip(tag_formfields, tag_dbattrs))

tag = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Tag, 
                    roles_accepted = ['superadmin', 'admin'],
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
                    )
tag.register()

