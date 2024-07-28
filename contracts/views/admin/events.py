###########################################################################################
# events - manage events and associated tables
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/09/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
events - manage events and associated tables
====================================================
'''

# standard
from re import match

# pypi
from flask import request, url_for
from flask.views import MethodView
from flask_login import login_required
from loutilities.tables import DbCrudApiRolePermissions
from loutilities.tables import REGEX_URL, SEPARATOR

# homegrown
from . import bp
from ...dbmodel import db, Event, Race, Client, State, Lead, Course, Service, Tag
from ...dbmodel import AddOn, FeeType, FeeBasedOn, EventAvailabilityException
from ...dbmodel import DateRule
from ...dbmodel import STATE_TENTATIVE
from ...apicommon import failure_response, success_response
from ...version import __docversion__
from ...daterule import daterule2dates
from .daterules import daterule
from .common import client
from .eventscontract import EventsContract

adminguide = f'https://contractility.readthedocs.io/en/{__docversion__}/contract-admin-event-guide.html'

##########################################################################################
# leads endpoint
###########################################################################################

lead_dbattrs = 'id,name,email,phone,roles,active'.split(',')
lead_formfields = 'rowid,name,email,phone,roles,active'.split(',')
lead_dbmapping = dict(list(zip(lead_dbattrs, lead_formfields)))
lead_formmapping = dict(list(zip(lead_formfields, lead_dbattrs)))

lead = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Lead, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'leads', 
                    endpoint = 'admin.leads', 
                    rule = '/leads', 
                    dbmapping = lead_dbmapping, 
                    formmapping = lead_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'name', 'name': 'name', 'label': 'Name', 
                          'className': 'field_req',
                        },
                        { 'data': 'email', 'name': 'email', 'label': 'Email', 
                          'className': 'field_req',
                        },
                        { 'data': 'phone', 'name': 'phone', 'label': 'Phone', 
                          'className': 'field_req',
                        },
                        { 'data': 'roles', 'name': 'roles', 'label': 'Roles', 'type': 'select2',
                          'options': ['finishline', 'coursemarking'],
                          'separator': SEPARATOR,   # separator is an Editor option, not select2 option
                          'opts': {'multiple': True}
                        },
                        { 'data': 'active', 'name': 'active', 'label': 'Active', 
                          'className': 'field_req',
                          '_treatment' : { 'boolean' : { 'formfield':'active', 'dbfield':'active' } }
                        },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'editRefresh'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                  },
                    )
lead.register()

##########################################################################################
# courses endpoint
###########################################################################################

course_dbattrs = 'id,course,address,isStandard'.split(',')
course_formfields = 'rowid,course,address,isStandard'.split(',')
course_dbmapping = dict(list(zip(course_dbattrs, course_formfields)))
course_formmapping = dict(list(zip(course_formfields, course_dbattrs)))

# update fields coming from client
course_dbmapping['isStandard'] = lambda formrow: formrow['isStandard'] == 'true'

course = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Course, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'courses', 
                    endpoint = 'admin.courses', 
                    rule = '/courses', 
                    dbmapping = course_dbmapping, 
                    formmapping = course_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'course', 'name': 'course', 'label': 'Course', '_unique':True,
                          'className': 'field_req',
                        },
                        { 'data': 'address', 'name': 'address', 'label': 'Address',
                          'className': 'field_req',
                        },
                        { 'data': 'isStandard', 'name': 'isStandard', 'label': 'Standard Course', 
                          'className': 'field_req',
                          '_treatment' : { 'boolean' : { 'formfield':'isStandard', 'dbfield':'isStandard' } }
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
                                        'lengthMenu': [ [-1, 10, 25, 50], ["All", 10, 25, 50] ],
                                  },
                    )
course.register()

##########################################################################################
# feetype endpoint
###########################################################################################

feetype_dbattrs = 'id,feeType,description'.split(',')
feetype_formfields = 'rowid,feeType,description'.split(',')
feetype_dbmapping = dict(list(zip(feetype_dbattrs, feetype_formfields)))
feetype_formmapping = dict(list(zip(feetype_formfields, feetype_dbattrs)))

feetype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = FeeType, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Fee Types', 
                    endpoint = 'admin.feetype', 
                    rule = '/feetype', 
                    dbmapping = feetype_dbmapping, 
                    formmapping = feetype_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'feeType', 'name': 'feeType', 'label': 'Fee Type', '_unique': True, 
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
feetype.register()

##########################################################################################
# feebasedon endpoint
###########################################################################################

feebasedon_dbattrs = 'id,service,fieldValue,fee'.split(',')
feebasedon_formfields = 'rowid,service,fieldValue,fee'.split(',')
feebasedon_dbmapping = dict(list(zip(feebasedon_dbattrs, feebasedon_formfields)))
feebasedon_formmapping = dict(list(zip(feebasedon_formfields, feebasedon_dbattrs)))

feebasedon = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = FeeBasedOn, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Fee Based On', 
                    endpoint = 'admin.feebasedon', 
                    rule = '/feebasedon', 
                    dbmapping = feebasedon_dbmapping, 
                    formmapping = feebasedon_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'service', 'name': 'service', 'label': 'Service',
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':Service, 'labelfield':'service', 'formfield':'service', 'dbfield':'service', 'uselist':False } },
                        },
                        { 'data': 'fieldValue', 'name': 'fieldValue', 'label': 'Field Value', 
                          'className': 'field_req',
                        },
                        { 'data': 'fee', 'name': 'fee', 'label': 'Fee', 
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
                                        'order': [['service.service:name', 'asc'], ['fieldValue:name', 'asc']],
                                  },
                    )
feebasedon.register()

##########################################################################################
# addon endpoint
###########################################################################################

addon_dbattrs = 'id,shortDescr,longDescr,fee'.split(',')
addon_formfields = 'rowid,shortDescr,longDescr,fee'.split(',')
addon_dbmapping = dict(list(zip(addon_dbattrs, addon_formfields)))
addon_formmapping = dict(list(zip(addon_formfields, addon_dbattrs)))

addon = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = AddOn, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Add-Ons', 
                    endpoint = 'admin.addon', 
                    rule = '/addon', 
                    dbmapping = addon_dbmapping, 
                    formmapping = addon_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'shortDescr', 'name': 'shortDescr', 'label': 'Add-on', '_unique': True, 
                          'className': 'field_req',
                        },
                        { 'data': 'longDescr', 'name': 'longDescr', 'label': 'Description', 
                          'className': 'field_req',
                        },
                        { 'data': 'fee', 'name': 'fee', 'label': 'Fee', 
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
addon.register()

###########################################################################################
# services endpoint
###########################################################################################

service_dbattrs = 'id,service,serviceLong,isCalendarBlocked,feeType,fee,basedOnField'.split(',')
service_formfields = 'rowid,service,serviceLong,isCalendarBlocked,feeType,fee,basedOnField'.split(',')
service_dbmapping = dict(list(zip(service_dbattrs, service_formfields)))
service_formmapping = dict(list(zip(service_formfields, service_dbattrs)))

service = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Service, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'services', 
                    endpoint = 'admin.services', 
                    rule = '/services', 
                    dbmapping = service_dbmapping, 
                    formmapping = service_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'service', 'name': 'service', 'label': 'Service', '_unique': True },
                        { 'data': 'serviceLong', 'name': 'serviceLong', 'label': 'Description',
                            'ed':{ 'label': 'Description (for contract)' }
                        },
                        { 'data': 'isCalendarBlocked', 'name': 'isCalendarBlocked', 'label': 'Blocks Calendar', 
                          '_treatment' : { 'boolean' : {'formfield':'isCalendarBlocked', 'dbfield':'isCalendarBlocked'} },
                        },
                        { 'data': 'feeType', 'name': 'feeType', 'label': 'Fee Type',
                          '_treatment' : { 'relationship' : { 'fieldmodel':FeeType, 'labelfield':'feeType', 'formfield':'feeType', 'dbfield':'feeType', 'uselist':False } }
                        },
                        { 'data': 'fee', 'name': 'fee', 'label': 'Fee' },
                        { 'data': 'basedOnField', 'name': 'basedOnField', 'label': 'Based on Field' },
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
service.register()

###########################################################################################
# eventexceptions endpoint
###########################################################################################

eventexception_dbattrs = 'id,shortDescr,exception,daterule,notes'.split(',')
eventexception_formfields = 'rowid,shortDescr,exception,daterule,notes'.split(',')
eventexception_dbmapping = dict(list(zip(eventexception_dbattrs, eventexception_formfields)))
eventexception_formmapping = dict(list(zip(eventexception_formfields, eventexception_dbattrs)))

eventexception = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = EventAvailabilityException, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'event exceptions', 
                    endpoint = 'admin.eventexceptions', 
                    rule = '/eventexceptions', 
                    dbmapping = eventexception_dbmapping, 
                    formmapping = eventexception_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'shortDescr', 'name': 'shortDescr', 'label': 'Name', '_unique': True, 
                          'className': 'field_req',
                        },
                        { 'data': 'daterule', 'name': 'daterule', 'label': 'Date Rule',
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':DateRule, 'labelfield':'rulename', 'formfield':'daterule', 
                                                              'dbfield':'daterule', 'uselist':False, 'searchbox':True,
                                                              'editable' : { 'api':daterule },
                                                            }
                                         }
                        },
                        { 'data': 'exception', 'name': 'exception', 'label': 'Exception', 'type': 'select2',
                          'className': 'field_req',
                          'options':['available', 'unavailable'], 
                          'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type':'textarea' },
                    ], 
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
eventexception.register()

###########################################################################################
# races endpoint
###########################################################################################

race_dbattrs = 'id,race,daterule,notes'.split(',')
race_formfields = 'rowid,race,daterule,notes'.split(',')
race_dbmapping = dict(list(zip(race_dbattrs, race_formfields)))
race_formmapping = dict(list(zip(race_formfields, race_dbattrs)))

race = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Race, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'races', 
                    endpoint = 'admin.races', 
                    rule = '/races', 
                    dbmapping = race_dbmapping, 
                    formmapping = race_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'race', 'name': 'race', 'label': 'Name', '_unique': True,
                          'className': 'field_req',
                        },
                        { 'data': 'daterule', 'name': 'daterule', 'label': 'Date Rule',
                          '_treatment' : { 'relationship' : { 'fieldmodel':DateRule, 'labelfield':'rulename', 'formfield':'daterule', 
                                                              'dbfield':'daterule', 'uselist':False, 'searchbox':True,
                                                              'editable' : { 'api':daterule },
                           } }
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type':'textarea' },
                    ], 
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
race.register()

###########################################################################################
# events endpoint
###########################################################################################

event_dbattrs =    ('id,race,date,state,eventUrl,registrationUrl,client,client.name,client.contactEmail,course,'
                    'lead,markinglead,mainStartTime,mainDistance,mainDistanceUnits,funStartTime,funDistance,funDistanceUnits,'
                    'services,finishersPrevYear,finishersCurrYear,maxParticipants,addOns,contractSentDate,'
                    'contractSignedDate,isContractUpdated,invoiceSentDate,isOnCalendar,tags,contractDocId,notes,'
                    'contractApprover,contractApproverEmail,contractApproverNotes'.split(','))
event_formfields = ('rowid,race,date,state,eventUrl,registrationUrl,client,client_name,client_email,course,'
                    'lead,markinglead,mainStartTime,mainDistance,mainDistanceUnits,funStartTime,funDistance,funDistanceUnits,'
                    'services,finishersPrevYear,finishersCurrYear,maxParticipants,addOns,contractSentDate,'
                    'contractSignedDate,isContractUpdated,invoiceSentDate,isOnCalendar,tags,contractDocId,notes,'
                    'contractApprover,contractApproverEmail,contractApproverNotes'.split(','))
event_dbmapping = dict(list(zip(event_dbattrs, event_formfields)))
event_formmapping = dict(list(zip(event_formfields, event_dbattrs)))
event_dbmapping['isContractUpdated'] = '__readonly__'
event_formmapping['isContractUpdated'] = lambda dbrow: 'yes' if dbrow.isContractUpdated else 'no'

## validate fields
def event_validate(action, formdata):
    results = []

    for field in ['date', 'invoiceSentDate']:
        if formdata[field] and not match(r"^(20|21)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$", formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid date: correct format is yyyy-mm-dd' })

    for field in ['mainStartTime', 'funStartTime']:
        if formdata[field] and not match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9] [ap]m$", formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid time: correct format is h:mm [am/pm]' })

    # regex patterns from http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
    for field in ['eventUrl', 'registrationUrl']:
        if formdata[field] and not match(REGEX_URL, formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid url: correct format is like http[s]://example.com' })

    # verify some fields were supplied
    for field in ['date']:
        if not formdata[field]:
            results.append({ 'name' : field, 'status' : 'please supply'})
    ## handle select fields
    for field in ['race', 'state', 'services', 'client']:
        if not formdata[field]['id']:
            results.append({ 'name' : '{}.id'.format(field), 'status' : 'please select'})

    return results

## yadcf external filters
filters = '\n'.join([
            "<div class='external-filter filter-container'>",
            "    <div class='filter-item'>",
            "        <span class='label'>State(s)</span>",
            "        <span id='external-filter-state' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>Date Range</span>",
            "        <span id='external-filter-dates' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>Service(s)</span>",
            "        <span id='external-filter-services' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>Tag(s)</span>",
            "        <span id='external-filter-tags' class='filter'></span>",
            "    </div>",
            "</div>",
            ])

## options for yadcf
yadcf_options = [
          {
           'column_selector': 'state.state:name', 
            'select_type': 'select2',
            'select_type_options': {
                'width': '150px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select states', 
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-state',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
          {
           'column_selector': 'date:name',
            'filter_type': 'range_date',
            'date_format': 'yyyy-mm-dd',
            'filter_container_id': 'external-filter-dates',
          },
          {
            'column_selector': 'services.service:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '200px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text' : 'Select services', 
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-services',
            'column_data_type': 'text',
            'text_data_delimiter': ', ',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
          {
            'column_selector': 'tags.tag:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '200px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text' : 'Select tags', 
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-tags',
            'column_data_type': 'text',
            'text_data_delimiter': ', ',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
    ]

def event_state_default():
    return State.query.filter_by(state=STATE_TENTATIVE).one().id

## finally the endpoint definition
event_view = EventsContract(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Event, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    serverside = False,
                    pagename = 'contract races', 
                    roles_accepted = ['super-admin', 'event-admin'],
                    template = 'events.superadmin.jinja2',
                    templateargs={'adminguide': adminguide},
                    endpoint = 'admin.events-superadmin', 
                    rule = '/events', 
                    dbmapping = event_dbmapping, 
                    formmapping = event_formmapping, 
                    pretablehtml = filters,
                    checkrequired = False,  # special checks in event_validate
                    clientcolumns = [
                        { 'data': 'race', 'name': 'race', 'label': 'Race', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':Race, 'labelfield':'race', 'formfield':'race', 
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                                                              'editable' : { 'api':race },
                                                            } 
                                         },
                        },
                        { 'data': 'date', 'name': 'date', 'label': 'Date', 'type':'datetime', 
                          'className': 'field_req',
                          'ed':{ 'label': 'Date (yyyy-mm-dd)', 'format':'YYYY-MM-DD', 
                          # first day of week for date picker is Sunday, strict date format required
                          'opts':{ 'momentStrict':True, 'firstDay':0 } },
                        },
                        { 'data': 'state', 'name': 'state', 'label': 'State', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':State, 'labelfield':'state', 'formfield':'state', 'dbfield':'state', 'uselist':False } },
                          # can't do this yet because need to evaluate callable 'def' in crudapi or tables
                          # 'ed':{ 'def':event_state_default }, 
                        },
                        { 'data': 'client', 'name': 'client', 'label': 'Client', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':Client, 'labelfield':'client', 'formfield':'client', 
                                                              'dbfield':'client', 'uselist':False, 'searchbox':True,
                                                              'editable' : { 'api':client },
                           } },
                        },
                        { 'data': 'client_name', 'name': 'client_name', 'label': 'Client Name', 'type':'readonly' },
                        { 'data': 'client_email', 'name': 'client_email', 'label': 'Client Email', 'type':'readonly' },
                        { 'data': 'eventUrl', 'name': 'eventUrl', 'label': 'Event URL' },
                        { 'data': 'registrationUrl', 'name': 'registrationUrl', 'label': 'Event Registration URL' },
                        { 'data': 'course', 'name': 'course', 'label': 'Course', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 
                                                             'fieldmodel':Course, 'labelfield':'course', 'formfield':'course', 
                                                             'dbfield':'course', 'uselist':False, 'searchbox':True,
                                                             'editable' : { 'api':course },
                                                            } 
                                         },
                        },
                        { 'data': 'mainStartTime', 'name': 'mainStartTime', 'label': 'Start Time', 
                          'className': 'field_req',
                          'type':'datetime', 'ed':{'format':'h:mm a', 'opts':{ 'momentStrict':True, 'minutesIncrement':15 }}, 
                        },
                        { 'data': 'mainDistance', 'name': 'mainDistance', 'label': 'Distance',
                          'className': 'field_req field_show_finishline field_show_coursemarking table_hide',
                        },
                        { 'data': 'mainDistanceUnits', 'name': 'mainDistanceUnits', 'label': 'Units', 'type': 'select2', 
                          'className': 'inhibitlabel field_show_finishline field_show_coursemarking table_hide', 
                          'options':['M', 'km'], 
                          'ed':{ 'def':'km' }, 
                          'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },
                        { 'data': 'funStartTime', 'name': 'funStartTime', 'label': 'Fun Run Start Time', 
                          'className': 'field_show_finishline field_show_coursemarking table_hide', 
                          'type':'datetime', 'ed':{'format':'h:mm a', 'opts':{ 'momentStrict':True, 'minutesIncrement':15 }}, 
                        },
                        { 'data': 'funDistance', 'name': 'funDistance', 'label': 'Fun Distance',
                          'className': 'field_show_finishline field_show_coursemarking table_hide', 
                        },
                        { 'data': 'funDistanceUnits', 'name': 'funDistanceUnits', 'label': 'Fun Units', 'type': 'select2',  
                          'className': 'inhibitlabel field_show_finishline field_show_coursemarking table_hide', 
                          'options':['M', 'km'], 'ed':{ 'def':'km' }, 'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },

                        { 'data': 'lead', 'name': 'lead', 'label': 'Lead', 
                          'className': 'field_req field_show_finishline', 
                          '_treatment' : { 'relationship' : { 'fieldmodel':Lead, 'labelfield':'name', 'formfield':'lead', 
                                                             'dbfield':'lead', 'uselist':False, 'nullable': True,
                                                             'queryfilters':[Lead.roles.like('%finishline%'), Lead.active==True]} },
                        },
                        { 'data': 'markinglead', 'name': 'markinglead', 'label': 'Marking Lead', 
                          'className': 'field_req field_show_coursemarking', 
                          '_treatment' : { 'relationship' : { 'fieldmodel':Lead, 'labelfield':'name', 'formfield':'markinglead', 
                                                             'dbfield':'markinglead', 'uselist':False, 'nullable': True,
                                                             'queryfilters':[Lead.roles.like('%coursemarking%'), Lead.active==True] } },
                        },
                        { 'data': 'services', 'name': 'services', 'label': 'Services', 
                          'className': 'field_req', 
                          '_treatment' : { 'relationship' : { 'fieldmodel':Service, 'labelfield':'service', 'formfield':'services', 'dbfield':'services', 'uselist':True, 'searchbox':False } },
                        },
                        { 'data': 'finishersPrevYear', 'name': 'finishersPrevYear', 'label': 'Prev Year #Finishers',
                          'className': 'field_show_finishline field_show_coursemarking table_hide', 
                        },
                        { 'data': 'finishersCurrYear', 'name': 'finishersCurrYear', 'label': 'Curr Year #Finishers',
                          'className': 'field_show_finishline field_show_coursemarking table_hide', 
                        },
                        { 'data': 'maxParticipants', 'name': 'maxParticipants', 
                          'label': 'Max Participants',
                          'className': 'field_req field_show_finishline field_show_coursemarking table_hide', 
                        },
                        { 'data': 'addOns', 'name': 'addOns', 'label': 'Add Ons', 
                          '_treatment' : { 'relationship' : { 'fieldmodel':AddOn, 'labelfield':'shortDescr', 'formfield':'addOns', 'dbfield':'addOns', 'uselist':True, 'searchbox':False } },
                        },
                        { 'data': 'invoiceSentDate', 'name': 'invoiceSentDate', 'label': 'Invoice Sent Date', 'type':'datetime', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Invoice Sent Date (yyyy-mm-dd)' }
                        },
                        { 'data': 'isOnCalendar', 'name': 'isOnCalendar', 'label': 'On Calendar', 
                          '_treatment' : {'boolean':{'formfield':'isOnCalendar', 'dbfield':'isOnCalendar'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'tags', 'name': 'tags', 'label': 'Tags', 
                          '_treatment' : { 'relationship' : { 'fieldmodel':Tag, 'labelfield':'tag', 'formfield':'tags', 'dbfield':'tags', 
                                                              'uselist':True, 'searchbox':False,
                                                              # TODO: requires fix for #80
                                                              # 'editable' : { 'api':tag },
                                                            }
                           },
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type': 'textarea',
                          'render': '$.fn.dataTable.render.ellipsis( 20 )',
                          },
                        { 'data': 'contractSentDate', 'name': 'contractSentDate', 'label': 'Contract Sent Date', 'type':'readonly' },
                        { 'data': 'contractDocId', 'name': 'contractDocId', 'label': 'Contract Doc', 'type':'googledoc', 'opts':{'text':'click for contract'},
                          'className': 'table_hide'
                          },
                        { 'data': 'isContractUpdated', 'name': 'isContractUpdated', 'label': 'Has Been Updated', 'type':'readonly' },
                        { 'data': 'contractSignedDate', 'name': 'contractSignedDate', 'label': 'Contract Signed Date', 'type':'readonly' },
                        { 'data': 'contractApprover', 'name': 'contractApprover', 'label': 'Approver', 'type':'readonly' },
                        { 'data': 'contractApproverEmail', 'name': 'contractApproverEmail', 'label': 'Approver Email', 'type':'readonly' },
                        { 'data': 'contractApproverNotes', 'name': 'contractApproverNotes', 'label': 'Approver Notes', 'type':'textarea',
                          'render': '$.fn.dataTable.render.ellipsis( 20 )',
                          },

                    ], 
                    validate = event_validate,
                    idSrc = 'rowid', 
                    buttons = lambda: ['create', 'editRefresh', 
                               {
                                    'extend': 'csv',
                                    'text': 'CSV',
                                    'exportOptions': {
                                        'columns': ':gt(0)',    # skip first column
                                        'orthogonal': 'export',
                                    }
                                },
                               {'name':'calendar', 'text':'Calendar', 'url':url_for('.calendar')},
                    ],
                        
                    dtoptions = {
                                    'scrollCollapse': True,
                                    'scrollX': True,
                                    'scrollXInner': "100%",
                                    'scrollY': True,
                                    'fixedColumns': {
                                                      'leftColumns': 3
                                                    },
                                    'order': [['date:name', 'desc']],
                                },
                    edoptions = {
                                    'template':'#customForm',
                                    'formOptions': { 'main': { 'focus': None } },
                                },
                    yadcfoptions = yadcf_options,
                    )
event_view.register()

class AjaxCheckDate(MethodView):
    decorators = [login_required]
    
    def get(self):
        race_id = request.args.get('race_id', None)
        date = request.args.get('date', None)
        if race_id and date:
            race = Race.query.filter_by(id=race_id).one()
            daterule = race.daterule
            year = int(date[0:4]) # ISO date yyyy-mm-dd
            daterule_dates = daterule2dates(daterule, year)
            # only look at first date in list
            if date != daterule_dates[0]:
                return failure_response(cause=f'Date "{date}" does not match daterule "{daterule.rulename}"')
            else:
                return success_response()
        else:
            return success_response()
bp.add_url_rule('/_checkdate',view_func=AjaxCheckDate.as_view('_checkdate'),methods=['GET'])

class AjaxGetClient(MethodView):
    decorators = [login_required]
    
    def get(self):
        client_id = request.args.get('client_id', None)
        if client_id:
            client = Client.query.filter_by(id=client_id).one()
            return success_response(client={'name': client.name, 'contactEmail': client.contactEmail})
        else:
            return success_response()
bp.add_url_rule('/_getclient',view_func=AjaxGetClient.as_view('_getclient'),methods=['GET'])
