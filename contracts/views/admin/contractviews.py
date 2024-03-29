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
from loutilities.tables import DbCrudApiRolePermissions

# homegrown
from . import bp
from ...dbmodel import db, Contract, ContractType, TemplateType, ContractBlockType
from ...version import __docversion__

adminguide = f'https://contractility.readthedocs.io/en/{__docversion__}/contract-admin-guide.html'

##########################################################################################
# templatetype endpoint
###########################################################################################

templatetype_dbattrs = 'id,templateType,description,contractType'.split(',')
templatetype_formfields = 'rowid,templateType,description,contractType'.split(',')
templatetype_dbmapping = dict(list(zip(templatetype_dbattrs, templatetype_formfields)))
templatetype_formmapping = dict(list(zip(templatetype_formfields, templatetype_dbattrs)))

templatetype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = TemplateType, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Template types', 
                    endpoint = 'admin.templatetypes', 
                    rule = '/templatetypes', 
                    dbmapping = templatetype_dbmapping, 
                    formmapping = templatetype_formmapping, 
                    clientcolumns = [
                        { 'data': 'templateType', 'name': 'templateType', 'label': 'Template Type' },
                        { 'data': 'description', 'name': 'description', 'label': 'Description' },
                        { 'data': 'contractType', 'name': 'contractType', 'label': 'Contract Type',
                                  '_treatment' : { 'relationship' : { 'fieldmodel':ContractType, 'labelfield':'contractType', 'formfield':'contractType', 'dbfield':'contractType', 'uselist':False, }
                                                 } },
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
templatetype.register()

##########################################################################################
# contracttype endpoint
###########################################################################################

contracttype_dbattrs = 'id,contractType,description'.split(',')
contracttype_formfields = 'rowid,contractType,description'.split(',')
contracttype_dbmapping = dict(list(zip(contracttype_dbattrs, contracttype_formfields)))
contracttype_formmapping = dict(list(zip(contracttype_formfields, contracttype_dbattrs)))

contracttype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = ContractType, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
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
                    buttons = ['create', 'editRefresh', 'remove'],
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
contractblocktype_dbmapping = dict(list(zip(contractblocktype_dbattrs, contractblocktype_formfields)))
contractblocktype_formmapping = dict(list(zip(contractblocktype_formfields, contractblocktype_dbattrs)))

contractblocktype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = ContractBlockType, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
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
                    buttons = ['create', 'editRefresh', 'remove'],
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
contract_dbmapping = dict(list(zip(contract_dbattrs, contract_formfields)))
contract_formmapping = dict(list(zip(contract_formfields, contract_dbattrs)))

contract = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Contract, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'contract content', 
                    endpoint = 'admin.contracts', 
                    rule = '/contractcontent', 
                    dbmapping = contract_dbmapping, 
                    formmapping = contract_formmapping, 
                    clientcolumns = [
                        { 'data': 'contractType', 'name': 'contractType', 'label': 'Contract Type',
                                  '_treatment' : { 'relationship' : { 'fieldmodel':ContractType, 'labelfield':'contractType', 'formfield':'contractType', 'dbfield':'contractType', 'uselist':False, }
                                                 } },
                        { 'data': 'templateType', 'name': 'templateType', 'label': 'Template Type',
                                  '_treatment' : { 'relationship' : { 'fieldmodel':TemplateType, 'labelfield':'templateType', 'formfield':'templateType', 'dbfield':'templateType', 'uselist':False, }
                                                 } },
                        { 'data': 'blockPriority', 'name': 'blockPriority', 'label': 'Priority' },
                        { 'data': 'contractBlockType', 'name': 'contractBlockType', 'label': 'Block Type',
                                  '_treatment' : { 'relationship' : { 'fieldmodel':ContractBlockType, 'labelfield':'blockType', 'formfield':'contractBlockType', 'dbfield':'contractBlockType', 'uselist':False, }
                                                 } },
                        { 'data': 'block', 'name': 'block', 'label': 'Block', 'type': 'textarea' },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'editRefresh', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                        'order': [
                                            ['contractType.contractType:name', 'asc'], 
                                            ['templateType.templateType:name', 'asc'],
                                            ['blockPriority:name', 'asc'],
                                        ],
                                  },
                    )
contract.register()
