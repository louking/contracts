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
from contracts.dbmodel import db, SponsorRace, SponsorLevel, SponsorBenefit, SponsorQueryLog
from contracts.crudapi import DbCrudApiRolePermissions
from contracts.crudapi import REGEX_URL, REGEX_EMAIL

##########################################################################################
# sponsorraces endpoint
###########################################################################################

sponsorrace_dbattrs = 'id,race,raceshort,racedirector,raceurl,sponsorurl,email,couponprovider,description'.split(',')
sponsorrace_formfields = 'rowid,race,raceshort,racedirector,raceurl,sponsorurl,email,couponprovider,description'.split(',')
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
# sponsorbenefits endpoint
###########################################################################################

sponsorbenefit_dbattrs = 'id,benefit,description,levels'.split(',')
sponsorbenefit_formfields = 'rowid,benefit,description,levels'.split(',')
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

