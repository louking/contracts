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
from flask_security import roles_accepted, current_user

# homegrown
from . import bp
from contracts.dbmodel import db, Event, Client, State, Lead, Course, Service, AddOn, FeeType, FeeBasedOn, EventAvailabilityException
from contracts.dbmodel import DateRule
from contracts.crudapi import DbCrudApiRolePermissions, DteDbRelationship, DteDbBool
from eventscontract import EventsApi

# https://www.regextester.com/93652 - modified to allow upper case
REGEX_URL = r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,5}(:[0-9]{1,5})?(\/.*)?$"

# https://www.regular-expressions.info/email.html
REGEX_EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$"

##########################################################################################
# states endpoint
###########################################################################################

state_dbattrs = 'id,state,description'.split(',')
state_formfields = 'rowid,state,description'.split(',')
state_dbmapping = dict(zip(state_dbattrs, state_formfields))
state_formmapping = dict(zip(state_formfields, state_dbattrs))

state = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = State, 
                    roles_accepted = ['superadmin'],
                    template = 'datatables.jinja2',
                    pagename = 'states', 
                    endpoint = 'admin.states', 
                    rule = '/states', 
                    dbmapping = state_dbmapping, 
                    formmapping = state_formmapping, 
                    clientcolumns = [
                        { 'data': 'state', 'name': 'state', 'label': 'State' },
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
state.register()

##########################################################################################
# leads endpoint
###########################################################################################

lead_dbattrs = 'id,name,email'.split(',')
lead_formfields = 'rowid,name,email'.split(',')
lead_dbmapping = dict(zip(lead_dbattrs, lead_formfields))
lead_formmapping = dict(zip(lead_formfields, lead_dbattrs))

lead = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Lead, 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'datatables.jinja2',
                    pagename = 'leads', 
                    endpoint = 'admin.leads', 
                    rule = '/leads', 
                    dbmapping = lead_dbmapping, 
                    formmapping = lead_formmapping, 
                    clientcolumns = [
                        { 'data': 'name', 'name': 'name', 'label': 'Name' },
                        { 'data': 'email', 'name': 'email', 'label': 'Email' },
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
lead.register()

##########################################################################################
# courses endpoint
###########################################################################################

course_dbattrs = 'id,course,address,isStandard'.split(',')
course_formfields = 'rowid,course,address,isStandard'.split(',')
course_dbmapping = dict(zip(course_dbattrs, course_formfields))
course_formmapping = dict(zip(course_formfields, course_dbattrs))

# update fields coming from client
course_dbmapping['isStandard'] = lambda formrow: formrow['isStandard'] == 'true'

course = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Course, 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'datatables.jinja2',
                    pagename = 'courses', 
                    endpoint = 'admin.courses', 
                    rule = '/courses', 
                    dbmapping = course_dbmapping, 
                    formmapping = course_formmapping, 
                    clientcolumns = [
                        { 'data': 'course', 'name': 'course', 'label': 'Course', '_unique':True },
                        { 'data': 'address', 'name': 'address', 'label': 'Address' },
                        { 'data': 'isStandard', 'name': 'isStandard', 'label': 'Standard Course', 
                          '_treatment' : { 'boolean' : { 'formfield':'isStandard', 'dbfield':'isStandard' } }
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
course.register()

##########################################################################################
# feetype endpoint
###########################################################################################

feetype_dbattrs = 'id,feeType,description'.split(',')
feetype_formfields = 'rowid,feeType,description'.split(',')
feetype_dbmapping = dict(zip(feetype_dbattrs, feetype_formfields))
feetype_formmapping = dict(zip(feetype_formfields, feetype_dbattrs))

feetype = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = FeeType, 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Fee Types', 
                    endpoint = 'admin.feetype', 
                    rule = '/feetype', 
                    dbmapping = feetype_dbmapping, 
                    formmapping = feetype_formmapping, 
                    clientcolumns = [
                        { 'data': 'feeType', 'name': 'feeType', 'label': 'Fee Type', '_unique': True },
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
feetype.register()

##########################################################################################
# feebasedon endpoint
###########################################################################################

feebasedon_dbattrs = 'id,service,fieldValue,fee'.split(',')
feebasedon_formfields = 'rowid,service,fieldValue,fee'.split(',')
feebasedon_dbmapping = dict(zip(feebasedon_dbattrs, feebasedon_formfields))
feebasedon_formmapping = dict(zip(feebasedon_formfields, feebasedon_dbattrs))

feebasedon = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = FeeBasedOn, 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Fee Based On', 
                    endpoint = 'admin.feebasedon', 
                    rule = '/feebasedon', 
                    dbmapping = feebasedon_dbmapping, 
                    formmapping = feebasedon_formmapping, 
                    clientcolumns = [
                        { 'data': 'service', 'name': 'service', 'label': 'Service',
                          '_treatment' : { 'relationship' : { 'model':Service, 'labelfield':'service', 'formfield':'service', 'dbfield':'service', 'uselist':False } },
                        },
                        { 'data': 'fieldValue', 'name': 'fieldValue', 'label': 'Field Value' },
                        { 'data': 'fee', 'name': 'fee', 'label': 'Fee' },
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
feebasedon.register()

##########################################################################################
# addon endpoint
###########################################################################################

addon_dbattrs = 'id,shortDescr,longDescr,fee'.split(',')
addon_formfields = 'rowid,shortDescr,longDescr,fee'.split(',')
addon_dbmapping = dict(zip(addon_dbattrs, addon_formfields))
addon_formmapping = dict(zip(addon_formfields, addon_dbattrs))

addon = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = AddOn, 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Add-Ons', 
                    endpoint = 'admin.addon', 
                    rule = '/addon', 
                    dbmapping = addon_dbmapping, 
                    formmapping = addon_formmapping, 
                    clientcolumns = [
                        { 'data': 'shortDescr', 'name': 'shortDescr', 'label': 'Add-on', '_unique': True },
                        { 'data': 'longDescr', 'name': 'longDescr', 'label': 'Description' },
                        { 'data': 'fee', 'name': 'fee', 'label': 'Fee' },
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
addon.register()

###########################################################################################
# services endpoint
###########################################################################################

service_dbattrs = 'id,service,serviceLong,isCalendarBlocked,feeType,fee,basedOnField'.split(',')
service_formfields = 'rowid,service,serviceLong,isCalendarBlocked,feeType,fee,basedOnField'.split(',')
service_dbmapping = dict(zip(service_dbattrs, service_formfields))
service_formmapping = dict(zip(service_formfields, service_dbattrs))

service = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Service, 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'datatables.jinja2',
                    pagename = 'services', 
                    endpoint = 'admin.services', 
                    rule = '/services', 
                    dbmapping = service_dbmapping, 
                    formmapping = service_formmapping, 
                    clientcolumns = [
                        { 'data': 'service', 'name': 'service', 'label': 'Service', '_unique': True },
                        { 'data': 'serviceLong', 'name': 'serviceLong', 'label': 'Description',
                            'ed':{ 'label': 'Description (for contract)' }
                        },
                        { 'data': 'isCalendarBlocked', 'name': 'isCalendarBlocked', 'label': 'Blocks Calendar', 
                          '_treatment' : { 'boolean' : {'formfield':'isCalendarBlocked', 'dbfield':'isCalendarBlocked'} },
                        },
                        { 'data': 'feeType', 'name': 'feeType', 'label': 'Fee Type',
                          '_treatment' : { 'relationship' : { 'model':FeeType, 'labelfield':'feeType', 'formfield':'feeType', 'dbfield':'feeType', 'uselist':False } }
                        },
                        { 'data': 'fee', 'name': 'fee', 'label': 'Fee' },
                        { 'data': 'basedOnField', 'name': 'basedOnField', 'label': 'Based on Field' },
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
service.register()

###########################################################################################
# eventexceptions endpoint
###########################################################################################

eventexception_dbattrs = 'id,shortDescr,exception,daterule,notes'.split(',')
eventexception_formfields = 'rowid,shortDescr,exception,daterule,notes'.split(',')
eventexception_dbmapping = dict(zip(eventexception_dbattrs, eventexception_formfields))
eventexception_formmapping = dict(zip(eventexception_formfields, eventexception_dbattrs))

eventexception = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = EventAvailabilityException, 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'datatables.jinja2',
                    pagename = 'eventexceptions', 
                    endpoint = 'admin.eventexceptions', 
                    rule = '/eventexceptions', 
                    dbmapping = eventexception_dbmapping, 
                    formmapping = eventexception_formmapping, 
                    clientcolumns = [
                        { 'data': 'shortDescr', 'name': 'shortDescr', 'label': 'Name', '_unique': True },
                        { 'data': 'daterule', 'name': 'daterule', 'label': 'Date Rule',
                          '_treatment' : { 'relationship' : { 'model':DateRule, 'labelfield':'rulename', 'formfield':'daterule', 'dbfield':'daterule', 'uselist':False } }
                        },
                        { 'data': 'exception', 'name': 'exception', 'label': 'Exception', 'type': 'select2',
                          'options':['available', 'unavailable'], 
                          'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type':'textarea' },
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
eventexception.register()

##########################################################################################
# clients endpoint
###########################################################################################

client_dbattrs = 'id,client,clientUrl,contactFirstName,contactFullName,contactEmail,clientPhone,clientAddr'.split(',')
client_formfields = 'rowid,client,clientUrl,contactFirstName,contactFullName,contactEmail,clientPhone,clientAddr'.split(',')
client_dbmapping = dict(zip(client_dbattrs, client_formfields))
client_formmapping = dict(zip(client_formfields, client_dbattrs))

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
                    pagename = 'clients', 
                    roles_accepted = ['admin'],
                    template = 'datatables.jinja2',
                    endpoint = 'admin.clients-admin', 
                    rule = '/clients', 
                    dbmapping = client_dbmapping, 
                    formmapping = client_formmapping, 
                    clientcolumns = [
                        { 'data': 'client', 'name': 'client', 'label': 'Client Name', '_unique':True },
                        { 'data': 'clientUrl', 'name': 'clientUrl', 'label': 'Client URL' },
                        { 'data': 'contactFirstName', 'name': 'contactFirstName', 'label': 'Contact First Name' },
                        { 'data': 'contactFullName', 'name': 'contactFullName', 'label': 'Contact Full Name' },
                        { 'data': 'contactEmail', 'name': 'contactEmail', 'label': 'Contact Email' },
                        { 'data': 'clientPhone', 'name': 'clientPhone', 'label': 'Client Phone' },
                        { 'data': 'clientAddr', 'name': 'clientAddr', 'label': 'Client Address', 'type': 'textarea' },
                    ], 
                    validate = client_validate,
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
client.register()

###########################################################################################
# events endpoint
###########################################################################################

event_dbattrs = 'id,event,date,state,eventUrl,registrationUrl,client,course,lead,mainStartTime,mainDistance,mainDistanceUnits,funStartTime,funDistance,funDistanceUnits,services,finishersPrevYear,finishersCurrYear,maxParticipants,addOns,contractSentDate,contractSignedDate,invoiceSentDate,paymentRecdDate,isOnCalendar,contractDocId,notes,contractApprover,contractApproverEmail,contractApproverNotes'.split(',')
event_formfields = 'rowid,event,date,state,eventUrl,registrationUrl,client,course,lead,mainStartTime,mainDistance,mainDistanceUnits,funStartTime,funDistance,funDistanceUnits,services,finishersPrevYear,finishersCurrYear,maxParticipants,addOns,contractSentDate,contractSignedDate,invoiceSentDate,paymentRecdDate,isOnCalendar,contractDocId,notes,contractApprover,contractApproverEmail,contractApproverNotes'.split(',')
event_dbmapping = dict(zip(event_dbattrs, event_formfields))
event_formmapping = dict(zip(event_formfields, event_dbattrs))

def event_validate(action, formdata):
    results = []

    for field in ['date', 'paymentRecdDate', 'invoiceSentDate']:
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
    for field in ['event', 'date']:
        if not formdata[field]:
            results.append({ 'name' : field, 'status' : 'please supply'})
    ## handle select fields
    for field in ['state', 'services', 'client']:
        if not formdata[field]['id']:
            results.append({ 'name' : '{}.id'.format(field), 'status' : 'please select'})

    return results

event = EventsApi(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Event, 
                    pagename = 'events', 
                    roles_accepted = ['superadmin', 'admin'],
                    template = 'events.superadmin.jinja2',
                    endpoint = 'admin.events-superadmin', 
                    rule = '/events', 
                    dbmapping = event_dbmapping, 
                    formmapping = event_formmapping, 
                    clientcolumns = [
                        { 'data': 'event', 'name': 'event', 'label': 'Event' },
                        { 'data': 'date', 'name': 'date', 'label': 'Date', 'type':'datetime', 
                            'ed':{ 'label': 'Date (yyyy-mm-dd)', 'format':'YYYY-MM-DD', 
                            # first day of week for date picker is Sunday, strict date format required
                            'opts':{ 'momentStrict':True, 'firstDay':0 } },
                        },
                        { 'data': 'state', 'name': 'state', 'label': 'State', 
                          '_treatment' : { 'relationship' : { 'model':State, 'labelfield':'state', 'formfield':'state', 'dbfield':'state', 'uselist':False } },
                          # can't do this because it's done at initialization so if database not filled yet this raises exception
                          # 'ed':{ 'def':State.query.filter_by(state='pending').one().id }, 
                        },
                        { 'data': 'client', 'name': 'client', 'label': 'Client', 
                          '_treatment' : { 'relationship' : { 'model':Client, 'labelfield':'client', 'formfield':'client', 'dbfield':'client', 'uselist':False,
                                                              'editable' : { 'api':client },
                           } },
                        },
                        { 'data': 'eventUrl', 'name': 'eventUrl', 'label': 'Event URL' },
                        { 'data': 'registrationUrl', 'name': 'registrationUrl', 'label': 'Event Registration URL' },
                        { 'data': 'course', 'name': 'course', 'label': 'Course', 
                          '_treatment' : { 'relationship' : { 
                                                             'model':Course, 'labelfield':'course', 'formfield':'course', 
                                                             'dbfield':'course', 'uselist':False, 'searchbox':True,
                                                             'editable' : { 'api':course },
                                                            } 
                                         },
                        },
                        { 'data': 'mainStartTime', 'name': 'mainStartTime', 'label': 'Start Time', 
                          'type':'datetime', 'ed':{'format':'h:mm a', 'opts':{ 'momentStrict':True, 'minutesIncrement':15 }}, 
                        },
                        { 'data': 'mainDistance', 'name': 'mainDistance', 'label': 'Distance' },
                        { 'data': 'mainDistanceUnits', 'name': 'mainDistanceUnits', 'label': 'Units', 'type': 'select2', 
                          'className': 'inhibitlabel', 
                          'options':['M', 'km'], 
                          'ed':{ 'def':'M' }, 
                          'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },
                        { 'data': 'funStartTime', 'name': 'funStartTime', 'label': 'Fun Run Start Time', 
                          'type':'datetime', 'ed':{'format':'h:mm a', 'opts':{ 'momentStrict':True, 'minutesIncrement':15 }}, 
                        },
                        { 'data': 'funDistance', 'name': 'funDistance', 'label': 'Fun Distance' },
                        { 'data': 'funDistanceUnits', 'name': 'funDistanceUnits', 'label': 'Fun Units', 'type': 'select2',  
                          'className': 'inhibitlabel', 
                          'options':['M', 'km'], 'ed':{ 'def':'M' }, 'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },

                        { 'data': 'lead', 'name': 'lead', 'label': 'Lead', 
                          '_treatment' : { 'relationship' : { 'model':Lead, 'labelfield':'name', 'formfield':'lead', 'dbfield':'lead', 'uselist':False } },
                        },
                        { 'data': 'services', 'name': 'services', 'label': 'Services', 
                          '_treatment' : { 'relationship' : { 'model':Service, 'labelfield':'service', 'formfield':'services', 'dbfield':'services', 'uselist':True, 'searchbox':False } },
                        },
                        { 'data': 'finishersPrevYear', 'name': 'finishersPrevYear', 'label': 'Prev Year #Finishers' },
                        { 'data': 'finishersCurrYear', 'name': 'finishersCurrYear', 'label': 'Curr Year #Finishers' },
                        { 'data': 'maxParticipants', 'name': 'maxParticipants', 'label': 'Max Participants' },
                        { 'data': 'addOns', 'name': 'addOns', 'label': 'Add Ons', 
                          '_treatment' : { 'relationship' : { 'model':AddOn, 'labelfield':'shortDescr', 'formfield':'addOns', 'dbfield':'addOns', 'uselist':True, 'searchbox':False } },
                        },
                        { 'data': 'paymentRecdDate', 'name': 'paymentRecdDate', 'label': 'Pymt Recd Date', 'type':'datetime', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Pymt Recd Date (yyyy-mm-dd)' }
                        },
                        { 'data': 'invoiceSentDate', 'name': 'invoiceSentDate', 'label': 'Invoice Sent Date', 'type':'datetime', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Invoice Sent Date (yyyy-mm-dd)' }
                        },
                        { 'data': 'isOnCalendar', 'name': 'isOnCalendar', 'label': 'On Calendar', 
                          '_treatment' : {'boolean':{'formfield':'isOnCalendar', 'dbfield':'isOnCalendar'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type': 'textarea' },
                        { 'data': 'contractSentDate', 'name': 'contractSentDate', 'label': 'Contract Sent Date', 'type':'readonly' },
                        { 'data': 'contractDocId', 'name': 'contractDocId', 'label': 'Contract Doc ID', 'type':'readonly' },
                        { 'data': 'contractSignedDate', 'name': 'contractSignedDate', 'label': 'Contract Signed Date', 'type':'readonly' },
                        { 'data': 'contractApprover', 'name': 'contractApprover', 'label': 'Approver', 'type':'readonly' },
                        { 'data': 'contractApproverEmail', 'name': 'contractApproverEmail', 'label': 'Approver Email', 'type':'readonly' },
                        { 'data': 'contractApproverNotes', 'name': 'contractApproverNotes', 'label': 'Approver Notes', 'type':'textarea' },

                    ], 
                    validate = event_validate,
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'edit', 'remove', 
                               # would use url_for('.calendar'), but this can't be done at until bp created
                               {'name':'calendar', 'text':'Calendar', 'url':'/admin/calendar'},
                    ],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                        'fixedColumns': {
                                                          'leftColumns': 3
                                                        },
                                        'order': [[2, 'asc']],
                                },
                    edoptions = {
                                        'template':'#customForm',
                                },
                    )
event.register()

