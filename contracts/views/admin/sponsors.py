###########################################################################################
# sponsors - manage sponsors and associated tables
#
#       Date            Author          Reason
#       ----            ------          ------
#       03/03/19        Lou King        Create
#
#   Copyright 2019 Lou King
#
###########################################################################################
'''
sponsors - manage sponsors and associated tables
====================================================
'''

# standard
from re import match

# pypi

# homegrown
from . import bp
from contracts.dbmodel import db, Sponsor, SponsorRace, SponsorLevel, SponsorBenefit
from contracts.dbmodel import SponsorQueryLog, SponsorRaceDate
from contracts.dbmodel import Client, State
from contracts.crudapi import DbCrudApiRolePermissions
from contracts.crudapi import REGEX_URL, REGEX_EMAIL
from common import client
from sponsorcontract import SponsorContract

##########################################################################################
# sponsors endpoint
###########################################################################################

sponsor_dbattrs = 'id,raceyear,racecontact,amount,couponcode,trend,contractDocId,race,client,state,level,datesolicited,dateagreed,invoicesent,isRegSiteUpdated,isWebsiteUpdated,isLogoReceived,isSponsorThankedFB,notes'.split(',')
sponsor_formfields = 'rowid,raceyear,racecontact,amount,couponcode,trend,contractDocId,race,client,state,level,datesolicited,dateagreed,invoicesent,isRegSiteUpdated,isWebsiteUpdated,isLogoReceived,isSponsorThankedFB,notes'.split(',')
sponsor_dbmapping = dict(zip(sponsor_dbattrs, sponsor_formfields))
sponsor_formmapping = dict(zip(sponsor_formfields, sponsor_dbattrs))

sponsor = SponsorContract(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Sponsor, 
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'sponsors.jinja2',
                    pagename = 'Sponsors', 
                    endpoint = 'admin.sponsors', 
                    rule = '/sponsors', 
                    dbmapping = sponsor_dbmapping, 
                    formmapping = sponsor_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'raceyear', 'name': 'raceyear', 'label': 'Race Year', 
                          'className': 'field_req',
                        },
                        { 'data': 'race', 'name': 'race', 'label': 'Race', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorRace, 'labelfield':'race', 'formfield':'race', 
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                           } }
                        },
                        { 'data': 'client', 'name': 'client', 'label': 'Client', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':Client, 'labelfield':'client', 'formfield':'client', 
                                                              'dbfield':'client', 'uselist':False, 'searchbox':True,
                                                              'editable' : { 'api':client },
                           } },
                        },
                        { 'data': 'state', 'name': 'state', 'label': 'State', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':State, 'labelfield':'state', 'formfield':'state', 'dbfield':'state', 'uselist':False } },
                          # can't do this yet because need to evaluate callable 'def' in crudapi or tables
                          # 'ed':{ 'def':event_state_default }, 
                        },
                        { 'data': 'level', 'name': 'level', 'label': 'Sponsorship Level', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorLevel, 'labelfield':'race_level', 'formfield':'level', 
                                                              'dbfield':'level', 'uselist':False, 'searchbox':True,
                           } }
                        },
                        { 'data': 'racecontact', 'name': 'racecontact', 'label': 'Race Contact', 
                          'className': 'field_req',
                        },
                        { 'data': 'amount', 'name': 'amount', 'label': 'Amount',
                          'className': 'field_req',
                        },
                        { 'data': 'couponcode', 'name': 'couponcode', 'label': 'Coupon Code', 
                          'className': 'field_req',
                        },
                        { 'data': 'trend', 'name': 'trend', 'label': 'Trend', 'type':'select2',
                          'className': 'field_req',
                          'options':['new','same','up','down'], 
                          'opts' : { 'minimumResultsForSearch': 'Infinity' },
                        },
                        { 'data': 'datesolicited', 'name': 'datesolicited', 'label': 'Date Solicited', 'type':'datetime', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Date Solicited (yyyy-mm-dd)' }
                        },
                        { 'data': 'dateagreed', 'name': 'dateagreed', 'label': 'Date Agreed', 'type':'datetime', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Date Agreed (yyyy-mm-dd)' }
                        },
                        { 'data': 'invoicesent', 'name': 'invoicesent', 'label': 'Invoice Sent', 'type':'datetime', 'dateFormat': 'yy-mm-dd',
                            'ed':{ 'label': 'Invoice Sent Date (yyyy-mm-dd)' }
                        },
                        { 'data': 'isRegSiteUpdated', 'name': 'isRegSiteUpdated', 'label': 'Registration Site Updated', 
                          'className': 'field_req',
                          '_treatment' : {'boolean':{'formfield':'isRegSiteUpdated', 'dbfield':'isRegSiteUpdated'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'isWebsiteUpdated', 'name': 'isWebsiteUpdated', 'label': 'Website Updated', 
                          'className': 'field_req',
                          '_treatment' : {'boolean':{'formfield':'isWebsiteUpdated', 'dbfield':'isWebsiteUpdated'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'isLogoReceived', 'name': 'isLogoReceived', 'label': 'Logo Received', 
                          'className': 'field_req',
                          '_treatment' : {'boolean':{'formfield':'isLogoReceived', 'dbfield':'isLogoReceived'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'isSponsorThankedFB', 'name': 'isSponsorThankedFB', 'label': 'Sponsor Thanked on FB', 
                          'className': 'field_req',
                          '_treatment' : {'boolean':{'formfield':'isSponsorThankedFB', 'dbfield':'isSponsorThankedFB'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'contractDocId', 'name': 'contractDocId', 'label': 'Agreement', 'type':'googledoc', 'opts':{'text':'click for contract'} },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type':'textarea'
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
                                    'fixedColumns': {
                                                      'leftColumns': 3,
                                                    },
                                  },
                    edoptions = {
                                    'template':'#customForm',
                                    'formOptions': { 'main': { 'focus': None } },
                                },
                    )
sponsor.register()

##########################################################################################
# sponsorraces endpoint
###########################################################################################

sponsorrace_dbattrs = 'id,race,raceshort,racedirector,rdphone,rdemail,isRDCertified,raceurl,sponsorurl,email,couponprovider,couponproviderid,description'.split(',')
sponsorrace_formfields = 'rowid,race,raceshort,racedirector,rdphone,rdemail,isRDCertified,raceurl,sponsorurl,email,couponprovider,couponproviderid,description'.split(',')
sponsorrace_dbmapping = dict(zip(sponsorrace_dbattrs, sponsorrace_formfields))
sponsorrace_formmapping = dict(zip(sponsorrace_formfields, sponsorrace_dbattrs))

def race_validate(action, formdata):
    results = []

    # regex patterns from http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
    for field in ['url']:
        if formdata[field] and not match(REGEX_URL, formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid url: correct format is like http[s]://example.com' })

    for field in ['email']:
        if formdata[field] and not match(REGEX_EMAIL, formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid email: correct format is like john.doe@example.com' })

    return results

sponsorrace = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorRace, 
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Sponsor Races', 
                    endpoint = 'admin.sponsorraces', 
                    rule = '/sponsorraces', 
                    dbmapping = sponsorrace_dbmapping, 
                    formmapping = sponsorrace_formmapping, 
                    checkrequired = True,
                    validate = race_validate,
                    clientcolumns = [
                        { 'data': 'race', 'name': 'race', 'label': 'Race', '_unique':True,
                          'className': 'field_req',
                        },
                        { 'data': 'raceshort', 'name': 'raceshort', 'label': 'Race Abbreviation', '_unique':True,
                          'className': 'field_req',
                        },
                        { 'data': 'racedirector', 'name': 'racedirector', 'label': 'Race Director', 
                          'className': 'field_req',
                        },
                        { 'data': 'rdphone', 'name': 'rdphone', 'label': 'Director Phone', 
                        },
                        { 'data': 'rdemail', 'name': 'rdemail', 'label': 'Director Email', 
                          'className': 'field_req',
                        },
                        { 'data': 'isRDCertified', 'name': 'isRDCertified', 'label': 'RD Is RRCA Certified', 
                          'className': 'field_req',
                          '_treatment' : {'boolean':{'formfield':'isRDCertified', 'dbfield':'isRDCertified'}},
                          'ed':{ 'def': 'no' }, 
                        },
                        { 'data': 'raceurl', 'name': 'raceurl', 'label': 'Race URL', 
                          'className': 'field_req',
                        },
                        { 'data': 'sponsorurl', 'name': 'sponsorurl', 'label': 'Sponsor URL', 
                          'className': 'field_req',
                        },
                        { 'data': 'email', 'name': 'email', 'label': 'Email', 
                          'className': 'field_req',
                        },
                        { 'data': 'couponprovider', 'name': 'couponprovider', 'label': 'Coupon Provider', 
                        },
                        { 'data': 'couponproviderid', 'name': 'couponproviderid', 'label': 'Coupon Provider ID', 
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description', 
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
                                        'fixedColumns': {
                                                          'leftColumns': 2,
                                                        },
                                  },
                    )
sponsorrace.register()

##########################################################################################
# sponsorlevels endpoint
###########################################################################################

sponsorlevel_dbattrs = 'id,race,level,minsponsorship,couponcount,maxallowed,description,display'.split(',')
sponsorlevel_formfields = 'rowid,race,level,minsponsorship,couponcount,maxallowed,description,display'.split(',')
sponsorlevel_dbmapping = dict(zip(sponsorlevel_dbattrs, sponsorlevel_formfields))
sponsorlevel_formmapping = dict(zip(sponsorlevel_formfields, sponsorlevel_dbattrs))

sponsorlevel = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorLevel, 
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Sponsor Levels', 
                    endpoint = 'admin.sponsorlevels', 
                    rule = '/sponsorlevels', 
                    dbmapping = sponsorlevel_dbmapping, 
                    formmapping = sponsorlevel_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'race', 'name': 'race', 'label': 'Race',
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorRace, 'labelfield':'race', 'formfield':'race', 
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                           } }
                        },
                        { 'data': 'minsponsorship', 'name': 'minsponsorship', 'label': 'Minimum $', 
                          'className': 'field_req',
                        },
                        { 'data': 'level', 'name': 'level', 'label': 'Level Name', 
                          'className': 'field_req',
                        },
                        { 'data': 'display', 'name': 'display', 'label': 'Display', 
                          'className': 'field_req',
                          '_treatment' : { 'boolean' : { 'formfield':'display', 'dbfield':'display' } },
                          'ed':{ 'def': 'yes' }, 
                        },
                        { 'data': 'maxallowed', 'name': 'maxallowed', 'label': 'Max Sponsors', 
                        },
                        { 'data': 'couponcount', 'name': 'couponcount', 'label': 'Num Free Entries', 
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description for Agreement', 
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
                                        'order': [[1, 'asc'], [2, 'desc']],
                                  },
                    )
sponsorlevel.register()

##########################################################################################
# sponsorracedates endpoint
###########################################################################################

sponsorracedate_dbattrs = 'id,race,raceyear,racedate'.split(',')
sponsorracedate_formfields = 'rowid,race,raceyear,racedate'.split(',')
sponsorracedate_dbmapping = dict(zip(sponsorracedate_dbattrs, sponsorracedate_formfields))
sponsorracedate_formmapping = dict(zip(sponsorracedate_formfields, sponsorracedate_dbattrs))

sponsorracedate = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorRaceDate, 
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Sponsor Race Dates', 
                    endpoint = 'admin.sponsorracedates', 
                    rule = '/sponsorracedates', 
                    dbmapping = sponsorracedate_dbmapping, 
                    formmapping = sponsorracedate_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'raceyear', 'name': 'raceyear', 'label': 'Race Year', 
                          'className': 'field_req',
                        },
                        { 'data': 'race', 'name': 'race', 'label': 'Race',
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorRace, 'labelfield':'race', 'formfield':'race', 
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                           } }
                        },
                        { 'data': 'racedate', 'name': 'racedate', 'label': 'Race Date', 'type': 'datetime',
                          'className': 'field_req',
                          'ed':{ 'label': 'Race Date (yyyy-mm-dd)' },
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
                                        'order': [[1, 'asc'], [2, 'desc']],
                                  },
                    )
sponsorracedate.register()

##########################################################################################
# sponsorbenefits endpoint
###########################################################################################

sponsorbenefit_dbattrs = 'id,order,benefit,description,levels'.split(',')
sponsorbenefit_formfields = 'rowid,order,benefit,description,levels'.split(',')
sponsorbenefit_dbmapping = dict(zip(sponsorbenefit_dbattrs, sponsorbenefit_formfields))
sponsorbenefit_formmapping = dict(zip(sponsorbenefit_formfields, sponsorbenefit_dbattrs))

sponsorbenefit = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorBenefit, 
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Sponsor Benefits', 
                    endpoint = 'admin.sponsorbenefits', 
                    rule = '/sponsorbenefits', 
                    dbmapping = sponsorbenefit_dbmapping, 
                    formmapping = sponsorbenefit_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'benefit', 'name': 'benefit', 'label': 'Benefit Name', 
                          'className': 'field_req',
                        },
                        { 'data': 'order', 'name': 'order', 'label': 'Agreement Order', 
                          'className': 'field_req',
                        },
                        { 'data': 'levels', 'name': 'levels', 'label': 'Levels', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorLevel, 'labelfield':'race_level', 'formfield':'levels', 
                                                              'dbfield':'levels', 'uselist':True, 'searchbox':True,
                           } }
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description for Agreement', 
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
                                        'order': [[2, 'asc']],
                                  },
                    )
sponsorbenefit.register()

##########################################################################################
# sponsorquerylogs endpoint
###########################################################################################

sponsorquerylog_dbattrs = 'id,time,organization,name,phone,city,state,street,zipcode,email,race,amount,level,comments'.split(',')
sponsorquerylog_formfields = 'rowid,time,organization,name,phone,city,state,street,zipcode,email,race,amount,level,comments'.split(',')
sponsorquerylog_dbmapping = dict(zip(sponsorquerylog_dbattrs, sponsorquerylog_formfields))
sponsorquerylog_formmapping = dict(zip(sponsorquerylog_formfields, sponsorquerylog_dbattrs))

sponsorquerylog = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorQueryLog, 
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'datatables.jinja2',
                    pagename = 'Sponsor Query Log', 
                    endpoint = 'admin.sponsorquerylog', 
                    rule = '/sponsorquerylog', 
                    dbmapping = sponsorquerylog_dbmapping, 
                    formmapping = sponsorquerylog_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'time', 'name': 'time', 'label': 'time', 'type': 'readonly' },
                        { 'data': 'organization', 'name': 'organization', 'label': 'organization', 'type': 'readonly' },
                        { 'data': 'name', 'name': 'name', 'label': 'name', 'type': 'readonly' },
                        { 'data': 'phone', 'name': 'phone', 'label': 'phone', 'type': 'readonly' },
                        { 'data': 'city', 'name': 'city', 'label': 'city', 'type': 'readonly' },
                        { 'data': 'state', 'name': 'state', 'label': 'state', 'type': 'readonly' },
                        { 'data': 'street', 'name': 'street', 'label': 'street', 'type': 'readonly' },
                        { 'data': 'zipcode', 'name': 'zipcode', 'label': 'zipcode', 'type': 'readonly' },
                        { 'data': 'email', 'name': 'email', 'label': 'email', 'type': 'readonly' },
                        { 'data': 'race', 'name': 'race', 'label': 'race', 'type': 'readonly' },
                        { 'data': 'amount', 'name': 'amount', 'label': 'amount', 'type': 'readonly' },
                        { 'data': 'level', 'name': 'level', 'label': 'level', 'type': 'readonly' },
                        { 'data': 'comments', 'name': 'comments', 'label': 'comments', 'type': 'textarea' },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = [ 
                                'edit',
                                'csv',
                    ],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                        'order': [[1, 'desc']],
                                  },
                    )
sponsorquerylog.register()

