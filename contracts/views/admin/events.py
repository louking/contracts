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
from contracts.dbmodel import db, Event, State, Lead, Course, Service, AddOn, FeeType
from contracts.crudapi import DbCrudApiRolePermissions, DteDbRelationship, DteDbBool
from contracts.request import addscripts

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
                        scriptfilter = addscripts,
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
                        scriptfilter = addscripts,
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
                        { 'data': 'course', 'name': 'course', 'label': 'Course' },
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
                        scriptfilter = addscripts,
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
                        { 'data': 'feeType', 'name': 'feeType', 'label': 'Fee Type' },
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
feetype.register()

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
                        { 'data': 'shortDescr', 'name': 'shortDescr', 'label': 'Add-on' },
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
                        scriptfilter = addscripts,
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
                        { 'data': 'service', 'name': 'service', 'label': 'Service' },
                        { 'data': 'serviceLong', 'name': 'serviceLong', 'label': 'Description',
                            'ed':{ 'label': 'Description (for contract)' }
                        },
                        { 'data': 'isCalendarBlocked', 'name': 'isCalendarBlocked', 'label': 'Blocks Calendar', 
                          '_treatment' : { 'boolean' : {'formfield':'isCalendarBlocked', 'dbfield':'isCalendarBlocked'} },
                        },
                        { 'data': 'feeType', 'name': 'feeType', 'label': 'Fee Type',
                          '_treatment' : { 'relationship' : { 'model':FeeType, 'modelfield':'feeType', 'formfield':'feeType', 'dbfield':'feeType', 'uselist':False } }
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
                        scriptfilter = addscripts,
                    )
service.register()

##########################################################################################
# events endpoint
###########################################################################################

event_dbattrs = 'id,event,date,state,eventUrl,course,lead,mainStartTime,mainDistance,mainDistanceUnits,funStartTime,funDistance,funDistanceUnits,organization,organizationUrl,contactFirstName,contactFullName,contactEmail,registrationUrl,services,finishersPrevYear,finishersCurrYear,maxParticipants,addOns,contractSentDate,contractSignedDate,invoiceSentDate,paymentRecdDate,isOnCalendar,contractDocId,notes'.split(',')
event_formfields = 'rowid,event,date,state,eventUrl,course,lead,mainStartTime,mainDistance,mainDistanceUnits,funStartTime,funDistance,funDistanceUnits,organization,organizationUrl,contactFirstName,contactFullName,contactEmail,registrationUrl,services,finishersPrevYear,finishersCurrYear,maxParticipants,addOns,contractSentDate,contractSignedDate,invoiceSentDate,paymentRecdDate,isOnCalendar,contractDocId,notes'.split(',')
event_dbmapping = dict(zip(event_dbattrs, event_formfields))
event_formmapping = dict(zip(event_formfields, event_dbattrs))

def event_validate(action, formdata):
    results = []

    for field in ['date', 'paymentRecdDate', 'invoiceSentDate']:
        if formdata[field] and not match(r"(20|21)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])", formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid date: correct format is yyyy-mm-dd' })

    for field in ['mainStartTime', 'funStartTime']:
        if formdata[field] and not match(r"([01]?[0-9]|2[0-3]):[0-5][0-9]", formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid time: correct format is h:mm' })

    for field in ['lead', 'state', 'course']:
        if not formdata[field]:
            results.append({'name' : field, 'status' : 'need to choose from list' })

    return results

event = DbCrudApiRolePermissions(
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
                        { 'data': 'date', 'name': 'date', 'label': 'Date', 'type':'date', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Date (yyyy-mm-dd)' }
                        },
                        # TODO: why did the following display a time widget?
                        # { 'data': 'date', 'name': 'date', 'label': 'Date', 'type':'datetime', 'ed':{'format':'yyyy-mm-dd'} },
                        { 'data': 'state', 'name': 'state', 'label': 'State', 
                          '_treatment' : { 'relationship' : { 'model':State, 'modelfield':'state', 'formfield':'state', 'dbfield':'state', 'uselist':False } },
                          'ed':{ 'def':'pending' }, 
                        },
                        { 'data': 'eventUrl', 'name': 'eventUrl', 'label': 'Event URL' },
                        { 'data': 'registrationUrl', 'name': 'registrationUrl', 'label': 'Event Registration URL' },
                        { 'data': 'course', 'name': 'course', 'label': 'Course', 
                          '_treatment' : { 'relationship' : { 
                                                             'model':Course, 'modelfield':'course', 'formfield':'course', 
                                                             'dbfield':'course', 'uselist':False, 'searchbox':True,
                                                             'editable' : { 'api':course, 'id':'eventcourse' },
                                                            } 
                                         },
                          'ed':{ 'def':'to be added' }, 
                        },
                        { 'data': 'mainStartTime', 'name': 'mainStartTime', 'label': 'Start Time',
                            'ed':{'format':'H:mm',
                                  'label' : 'Start Time (h:mm) h=0-23'
                            } 
                        },
                        { 'data': 'mainDistance', 'name': 'mainDistance', 'label': 'Distance' },
                        { 'data': 'mainDistanceUnits', 'name': 'mainDistanceUnits', 'label': 'Units', 'type': 'select2',  
                          'options':['M', 'km'], 
                          'ed':{ 'def':'M' }, 
                          'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },
                        { 'data': 'funStartTime', 'name': 'funStartTime', 'label': 'Fun Run Start Time', 
                            'ed':{'format':'H:mm',
                                  'label' : 'Fun Start Time (h:mm) h=0-23'
                            } 
                        },
                        { 'data': 'funDistance', 'name': 'funDistance', 'label': 'Fun Distance' },
                        { 'data': 'funDistanceUnits', 'name': 'funDistanceUnits', 'label': 'Fun Units', 'type': 'select2',  
                          'options':['M', 'km'], 'ed':{ 'def':'M' }, 'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },
                        { 'data': 'organization', 'name': 'organization', 'label': 'Organization Name' },
                        { 'data': 'organizationUrl', 'name': 'organizationUrl', 'label': 'Organization URL' },
                        { 'data': 'contactFirstName', 'name': 'contactFirstName', 'label': 'Contact First Name' },
                        { 'data': 'contactFullName', 'name': 'contactFullName', 'label': 'Contact Name' },
                        { 'data': 'contactEmail', 'name': 'contactEmail', 'label': 'Contact Email' },
                        { 'data': 'lead', 'name': 'lead', 'label': 'Lead', 
                          '_treatment' : { 'relationship' : { 'model':Lead, 'modelfield':'name', 'formfield':'lead', 'dbfield':'lead', 'uselist':False } },
                          'ed':{ 'def':'to be added' }, 
                        },
                        { 'data': 'services', 'name': 'services', 'label': 'Services', 
                          '_treatment' : { 'relationship' : { 'model':Service, 'modelfield':'service', 'formfield':'services', 'dbfield':'services', 'uselist':True, 'searchbox':False } },
                        },
                        { 'data': 'finishersPrevYear', 'name': 'finishersPrevYear', 'label': 'Prev Year #Finishers' },
                        { 'data': 'finishersCurrYear', 'name': 'finishersCurrYear', 'label': 'Curr Year #Finishers' },
                        { 'data': 'maxParticipants', 'name': 'maxParticipants', 'label': 'Max Participants' },
                        { 'data': 'addOns', 'name': 'addOns', 'label': 'Add Ons', 
                          '_treatment' : { 'relationship' : { 'model':AddOn, 'modelfield':'shortDescr', 'formfield':'addOns', 'dbfield':'addOns', 'uselist':True, 'searchbox':False } },
                        },
                        { 'data': 'paymentRecdDate', 'name': 'paymentRecdDate', 'label': 'Pymt Recd Date', 'type':'date', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Pymt Recd Date (yyyy-mm-dd)' }
                        },
                        { 'data': 'invoiceSentDate', 'name': 'invoiceSentDate', 'label': 'Invoice Sent Date', 'type':'date', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Invoice Sent Date (yyyy-mm-dd)' }
                        },
                        { 'data': 'isOnCalendar', 'name': 'isOnCalendar', 'label': 'On Calendar', 
                          '_treatment' : {'boolean':{'formfield':'isOnCalendar', 'dbfield':'isOnCalendar'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type': 'textarea' },
                        { 'data': 'contractSentDate', 'name': 'contractSentDate', 'label': 'Contract Sent Date', 'type':'readonly' },
                        { 'data': 'contractSignedDate', 'name': 'contractSignedDate', 'label': 'Contract Signed Date', 'type':'readonly' },
                        { 'data': 'contractDocId', 'name': 'contractDocId', 'label': 'Contract Doc ID', 'type':'readonly' },

                    ], 
                    validate = event_validate,
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'edit', 'remove'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                        'fixedColumns': {
                                                          'leftColumns': 3
                                                        },
                                },
                    edoptions = {
                                        'template':'#customForm',
                                },
                    pagejsfiles = ['events.js'],
                    pagecssfiles = ['editor-forms.css'],
                    scriptfilter = addscripts,
                    # templateargs = {'saformjsurls': 
                    #                     lambda: 
                    #                       [ course.saformurl('course', 'eventcourse'), 
                    #                         lead.saformurl('lead', 'eventlead'), 
                    #                       ] }
                    )
event.register()

