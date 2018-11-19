###########################################################################################
# contracts - contracts views
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/13/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
contract - class and helpers to manage contract
==================================================
'''

# standard

# pypy

# homegrown
from . import bp
from contracts.dbmodel import db, Contract, ContractType, TemplateType, ContractBlockType
from contracts.crudapi import DbCrudApiRolePermissions, DteDbRelationship

##########################################################################################
# templatetype endpoint
###########################################################################################

templatetype_dbattrs = 'id,templateType,description,contractType'.split(',')
templatetype_formfields = 'rowid,templateType,description,contractType'.split(',')
templatetype_dbmapping = dict(zip(templatetype_dbattrs, templatetype_formfields))
templatetype_formmapping = dict(zip(templatetype_formfields, templatetype_dbattrs))

templatetype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = TemplateType, 
                    roles_accepted = ['superadmin'],
                    template = 'datatables.jinja2',
                    pagename = 'Template types', 
                    endpoint = 'admin.templatetypes', 
                    rule = '/templatetypes', 
                    dbmapping = templatetype_dbmapping, 
                    formmapping = templatetype_formmapping, 
                    clientcolumns = [
                        { 'data': 'templateType', 'name': 'templateType', 'label': 'Template Type' },
                        { 'data': 'description', 'name': 'description', 'label': 'Description' },
                        { 'data': 'contractType', 'name': 'contractType', 'label': 'Contract Type',
                                  '_treatment' : { 'relationship' : { 'model':ContractType, 'labelfield':'contractType', 'formfield':'contractType', 'dbfield':'contractType', 'uselist':False, }
                                                 } },
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
templatetype.register()

##########################################################################################
# contracttype endpoint
###########################################################################################

contracttype_dbattrs = 'id,contractType,description'.split(',')
contracttype_formfields = 'rowid,contractType,description'.split(',')
contracttype_dbmapping = dict(zip(contracttype_dbattrs, contracttype_formfields))
contracttype_formmapping = dict(zip(contracttype_formfields, contracttype_dbattrs))

contracttype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = ContractType, 
                    roles_accepted = ['superadmin'],
                    template = 'datatables.jinja2',
                    pagename = 'contracttypes', 
                    endpoint = 'admin.contracttypes', 
                    rule = '/contracttypes', 
                    dbmapping = contracttype_dbmapping, 
                    formmapping = contracttype_formmapping, 
                    clientcolumns = [
                        { 'data': 'contractType', 'name': 'contractType', 'label': 'Contract Type' },
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
                    )
contracttype.register()

##########################################################################################
# contractblocktype endpoint
###########################################################################################

contractblocktype_dbattrs = 'id,blockType,description'.split(',')
contractblocktype_formfields = 'rowid,blockType,description'.split(',')
contractblocktype_dbmapping = dict(zip(contractblocktype_dbattrs, contractblocktype_formfields))
contractblocktype_formmapping = dict(zip(contractblocktype_formfields, contractblocktype_dbattrs))

contractblocktype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = ContractBlockType, 
                    roles_accepted = ['superadmin'],
                    template = 'datatables.jinja2',
                    pagename = 'contractblocktypes', 
                    endpoint = 'admin.contractblocktypes', 
                    rule = '/contractblocktypes', 
                    dbmapping = contractblocktype_dbmapping, 
                    formmapping = contractblocktype_formmapping, 
                    clientcolumns = [
                        { 'data': 'blockType', 'name': 'blockType', 'label': 'Block Type' },
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
                    )
contractblocktype.register()

##########################################################################################
# contract endpoint
###########################################################################################

contract_dbattrs = 'id,contractType,templateType,blockPriority,contractBlockType,block'.split(',')
contract_formfields = 'rowid,contractType,templateType,blockPriority,contractBlockType,block'.split(',')
contract_dbmapping = dict(zip(contract_dbattrs, contract_formfields))
contract_formmapping = dict(zip(contract_formfields, contract_dbattrs))

contract = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Contract, 
                    roles_accepted = ['superadmin'],
                    template = 'datatables.jinja2',
                    pagename = 'contracts', 
                    endpoint = 'admin.contracts', 
                    rule = '/contracts', 
                    dbmapping = contract_dbmapping, 
                    formmapping = contract_formmapping, 
                    clientcolumns = [
                        { 'data': 'contractType', 'name': 'contractType', 'label': 'Contract Type',
                                  '_treatment' : { 'relationship' : { 'model':ContractType, 'labelfield':'contractType', 'formfield':'contractType', 'dbfield':'contractType', 'uselist':False, }
                                                 } },
                        { 'data': 'templateType', 'name': 'templateType', 'label': 'Template Type',
                                  '_treatment' : { 'relationship' : { 'model':TemplateType, 'labelfield':'templateType', 'formfield':'templateType', 'dbfield':'templateType', 'uselist':False, }
                                                 } },
                        { 'data': 'blockPriority', 'name': 'blockPriority', 'label': 'Priority' },
                        { 'data': 'contractBlockType', 'name': 'contractBlockType', 'label': 'Block Type',
                                  '_treatment' : { 'relationship' : { 'model':ContractBlockType, 'labelfield':'blockType', 'formfield':'contractBlockType', 'dbfield':'contractBlockType', 'uselist':False, }
                                                 } },
                        { 'data': 'block', 'name': 'block', 'label': 'Block', 'type': 'textarea' },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'edit', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                        'order': [[1, 'asc'], [2, 'asc']],
                                  },
                    )
contract.register()
