###########################################################################################
# daterules - manage daterules tables
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/12/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
daterules - manage daterules tables
====================================================
'''

# pypi
from flask import current_app
from loutilities.tables import DbCrudApiRolePermissions, DataTablesEditor

# homegrown
from . import bp
from ...dbmodel import db, DateRule
from ...version import __docversion__

adminguide = f'https://contractility.readthedocs.io/en/{__docversion__}/contract-admin-event-guide.html'

##########################################################################################
# daterules endpoint
###########################################################################################

daterule_dbattrs = 'id,rulename,rule,day,month,date,year,deltaday,addldays'.split(',')
daterule_formfields = 'rowid,rulename,rule,day,month,date,year,deltaday,addldays'.split(',')
daterule_dbmapping = dict(list(zip(daterule_dbattrs, daterule_formfields)))
daterule_formmapping = dict(list(zip(daterule_formfields, daterule_dbattrs)))

# set up rulename based on DateRule.__init__() logic
def set_rulename(formrow):
    # make initial conversion from inrow to dbrow
    dte = DataTablesEditor(daterule_formmapping, daterule_dbmapping)
    tmpdbrow = DateRule()
    dte.set_dbrow(formrow, tmpdbrow)
    
    # create new instance of dbrow without setting rulename apriori
    # this sets rulename per DateRule.__init__()
    tmpdbrow.rulename = ''
    newdbrow = DateRule(**{k:v for k,v in list(tmpdbrow.__dict__.items()) if k[0] != '_'})
    current_app.logger.debug('set_rulename(): tmpdbrow.__dict__ = {}'.format(tmpdbrow.__dict__))

    # use the rulename which was created
    return newdbrow.rulename
daterule_dbmapping['rulename'] = set_rulename

def daterule_validate(action, formdata):
    results = []
    
    # see if row exists with same rule
    rulename = set_rulename(formdata)
    row = DateRule.query.filter_by(rulename=rulename).one_or_none()

    # indicate error on rule field, as rulename field is hidden
    if row:
        results.append({'name':'rule', 'status':'fields indicate duplicate rule: {}'.format(rulename)})

    return results

daterule = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = DateRule, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Date Rules', 
                    endpoint = 'admin.daterules', 
                    rule = '/daterules', 
                    dbmapping = daterule_dbmapping, 
                    formmapping = daterule_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'rulename', 'name': 'rulename', 'label': 'Rule Name', 'ed':{'type':'hidden'} },
                        { 'data': 'rule', 'name': 'rule', 'label': 'Rule', 'type': 'select2',
                          # see https://stackoverflow.com/questions/47770592/how-to-get-all-the-column-names-their-types-including-enum-and-its-possible
                          'className': 'field_req',
                          'options': DateRule.__table__.columns['rule'].type.enums, 
                        },
                        { 'data': 'day', 'name': 'day', 'label': 'Day of Week', 'type':'select2',
                          'options': DateRule.__table__.columns['day'].type.enums, 
                        },
                        { 'data': 'month', 'name': 'month', 'label': 'Month', 'type': 'select2',
                          'options': DateRule.__table__.columns['month'].type.enums, 
                        },
                        { 'data': 'deltaday', 'name': 'deltaday', 'label': 'Offset Days', 'message':'number of days before (negative) or after (positive)' },
                        { 'data': 'addldays', 'name': 'addldays', 'label': 'Additional Days', 'message':'include days before (negative) or after (positive)' },
                        { 'data': 'date', 'name': 'date', 'label': 'Date' },
                        { 'data': 'year', 'name': 'year', 'label': 'Year' },
                    ], 
                    validate = daterule_validate,
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
daterule.register()

