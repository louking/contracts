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
from html import escape

# pypi
from flask import request, url_for, flash
from dominate.tags import button
from pytz import all_timezones
from loutilities.tables import DbCrudApiRolePermissions, DteDbDependent
from loutilities.tables import REGEX_URL, REGEX_VBL
from loutilities.filters import filtercontainerdiv, filterdiv

# allow name <email> format. TODO: update loutilities.tables to use this regex
REGEX_EMAIL = r'^(?:"?)(\b[A-Za-z]+\b ?)*(?:"?) ?<([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)>|([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)$'

# homegrown
from . import bp
from ...dbmodel import db, Sponsor, SponsorRace, SponsorLevel, SponsorBenefit, SponsorTag
from ...dbmodel import SponsorQueryLog, SponsorRaceDate, SponsorRaceVbl
from ...dbmodel import Client, State
from .common import client
from .sponsorcontract import SponsorContract
from ...trends import check_sponsorship_conflicts, render_sponsorship_conflicts
from ...version import __docversion__

adminguide = f'https://contractility.readthedocs.io/en/{__docversion__}/contract-admin-sponsor-guide.html'

##########################################################################################
# sponsors endpoint
###########################################################################################

sponsor_dbattrs = 'id,raceyear,racecontact,amount,couponcode,trend,contractDocId,race,client,client.name,client.contactEmail,client.clientAddr,state,level,datesolicited,dateagreed,invoicesent,RegSiteUpdated,isWebsiteUpdated,isLogoReceived,isSponsorThankedFB,tags,notes'.split(',')
sponsor_formfields = 'rowid,raceyear,racecontact,amount,couponcode,trend,contractDocId,race,client,client_name,client_email,client_addr,state,level,datesolicited,dateagreed,invoicesent,RegSiteUpdated,isWebsiteUpdated,isLogoReceived,isSponsorThankedFB,tags,notes'.split(',')
sponsor_dbmapping = dict(list(zip(sponsor_dbattrs, sponsor_formfields)))
sponsor_formmapping = dict(list(zip(sponsor_formfields, sponsor_dbattrs)))

## yadcf external filters
sponsor_filters = '\n'.join([
            "<div class='external-filter filter-container'>",
            "    <div class='filter-item'>",
            "        <span class='label'>Race Year</span>",
            "        <span id='external-filter-raceyear' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>Race</span>",
            "        <span id='external-filter-race' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>State(s)</span>",
            "        <span id='external-filter-state' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>Level(s)</span>",
            "        <span id='external-filter-levels' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>Trend(s)</span>",
            "        <span id='external-filter-trends' class='filter'></span>",
            "    </div>",
            "",
            "    <div class='filter-item'>",
            "        <span class='label'>Tag(s)</span>",
            "        <span id='external-filter-tags' class='filter'></span>",
            "    </div>",
            "</div>",
            ])

## options for yadcf
sponsor_yadcf_options = [
          {
           'column_selector': 'raceyear:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '100px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select race year', 
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-raceyear',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
          {
           'column_selector': 'race.race:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '300px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select race', 
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-race',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
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
            'column_selector': 'level.race_level:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '200px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text' : 'Select levels', 
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-levels',
            'filter_match_mode': 'exact',
            'column_data_type': 'text',
            'text_data_delimiter': ', ',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
          {
            'column_selector': 'trend:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '200px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text' : 'Select trends', 
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-trends',
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
                      'id': -1,
                      'text': 'Select tags',
                  },
              },
              'filter_type': 'multi_select',
              'filter_container_id': 'external-filter-tags',
              'column_data_type': 'text',
              'text_data_delimiter': ', ',
              'filter_reset_button_text': False,  # hide yadcf reset button
          },
]

def sponsor_validate(action, formdata):
    results = []

    # verify some fields were supplied
    for field in ['couponcode']:
        level = SponsorLevel.query.filter_by(id=formdata['level']['id']).one_or_none()
        if level and level.couponcount and level.couponcount > 0:
            if not formdata[field]:
                results.append({ 'name' : field, 'status' : 'please supply'})

    return results


sponsor_view = SponsorContract(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Sponsor, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'sponsors.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Sponsorships', 
                    endpoint = 'admin.sponsorships', 
                    rule = '/sponsorships', 
                    dbmapping = sponsor_dbmapping, 
                    formmapping = sponsor_formmapping, 
                    checkrequired = True,
                    validate = sponsor_validate,
                    clientcolumns = [
                        { 'data': 'raceyear', 'name': 'raceyear', 'label': 'Race Year', 
                          'className': 'field_req',
                        },
                        { 'data': 'race', 'name': 'race', 'label': 'Race', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorRace, 'labelfield':'race', 'formfield':'race', 
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                           } },
                           '_update' : {'options': 
                                DteDbDependent(
                                               model=SponsorRace, 
                                               modelfield='id',
                                               depmodel=SponsorLevel, 
                                               depmodelref='race_id',
                                               depmodelfield='race_level', 
                                               depformfield='level.id', # <dependentfield>.<relationship valuefield, default 'id'>
                                               depvaluefield='id', 
                                               )
                           },

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
                        { 'data': 'amount', 'name': 'amount', 'label': 'Amount',
                          'className': 'field_req',
                        },
                        { 'data': 'client_name', 'name': 'client_name', 'label': 'Client Name', 'type': 'readonly',
                        },
                        { 'data': 'client_email', 'name': 'client_email', 'label': 'Client Email', 'type': 'readonly',
                        },
                        { 'data': 'client_addr', 'name': 'client_addr', 'label': 'Client Addr', 'type': 'readonly',
                        },
                        { 'data': 'racecontact', 'name': 'racecontact', 'label': 'Race Contact', 
                          'className': 'field_req',
                        },
                        { 'data': 'couponcode', 'name': 'couponcode', 'label': 'Coupon Code', 
                        },
                        { 'data': 'trend', 'name': 'trend', 'label': 'Trend', 'type':'readonly',
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
                        { 'data': 'RegSiteUpdated', 'name': 'RegSiteUpdated', 'label': 'Registration Site Updated', 
                          'type': 'select2',
                          'options':['no', 'yes', 'n/a'], 
                          'ed':{ 'def': 'no' }, 
                          'className': 'field_req',
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
                        { 'data': 'contractDocId', 'name': 'contractDocId', 'label': 'Agreement', 'type':'googledoc', 'opts':{'text':'click for contract'},
                          'render': '$.fn.dataTable.render.ellipsis( 10 )',
                          },
                        { 'data': 'tags', 'name': 'tags', 'label': 'Tags',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorTag, 'labelfield':'tag', 'formfield':'tags', 'dbfield':'tags',
                                                              'uselist':True, 'searchbox':False,
                                                              # TODO: requires fix for #80
                                                              # 'editable' : { 'api':tag },
                                                            }
                           },
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type':'textarea',
                          'render': '$.fn.dataTable.render.ellipsis( 20 )',
                        },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'editRefresh', 
                               {
                                    'extend': 'csv',
                                    'text': 'CSV',
                                    'exportOptions': {
                                        'columns': ':gt(0)',    # skip first column
                                    }
                                }
                            ],
                    dtoptions = {
                                    'scrollCollapse': True,
                                    'scrollX': True,
                                    'scrollXInner': "100%",
                                    'scrollY': True,
                                    'lengthMenu': [ [-1, 10, 25, 50], ["All", 10, 25, 50] ],
                                    'fixedColumns': {
                                                      'leftColumns': 4,
                                                    },
                                  },
                    edoptions = {
                                    'template':'#customForm',
                                    'formOptions': { 'main': { 'focus': None } },
                                },
                    pretablehtml = sponsor_filters,
                    yadcfoptions = sponsor_yadcf_options,
                    )
sponsor_view.register()

##########################################################################################
# sponsorviews endpoint
###########################################################################################

sponsorview_dbattrs = 'id,raceyear,racecontact,amount,trend,contractDocId,race.race,client.client,' \
                      'client.name,client.contactEmail,state.state,level.race_level,notes'.split(',')
sponsorview_formfields = 'rowid,raceyear,racecontact,amount,trend,contractDocId,race,client,' \
                         'client_name,client_email,state,level,notes'.split(',')
sponsorview_dbmapping = dict(list(zip(sponsorview_dbattrs, sponsorview_formfields)))
sponsorview_formmapping = dict(list(zip(sponsorview_formfields, sponsorview_dbattrs)))

## yadcf external filters
sponsorview_filters = filtercontainerdiv()
with sponsorview_filters:
    # need loutilities-3.4 to call this as a function, hack below until url_for can be used
    # button('Summary', url=url_for('admin.sponsorsummaryview', id='sponsordetails-summary-button', style='margin-right:5px;'))
    button('Summary', url='/admin/sponsorsummaryview', id='sponsordetails-summary-button', style='margin-right:5px;')
    filterdiv('external-filter-raceyear', 'Race Year')
    filterdiv('external-filter-state', 'State(s)')
    filterdiv('external-filter-levels', 'Level(s)')
    filterdiv('external-filter-trends', 'Trend(s)')

## options for yadcf
raceyearcol = 1
statecol = 4
levelcol = 5
trendcol = 8
sponsorview_yadcf_options = [
          {
           'column_selector': 'raceyear:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '100px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select race year', 
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-raceyear',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
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
            'column_selector': 'level.race_level:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '200px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text' : 'Select levels', 
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-levels',
            'filter_match_mode': 'exact',
            'column_data_type': 'text',
            'text_data_delimiter': ', ',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
          {
            'column_selector': 'trend:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '200px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text' : 'Select trends', 
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-trends',
            'column_data_type': 'text',
            'text_data_delimiter': ', ',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
    ]

class ViewkeyView(DbCrudApiRolePermissions):
    def permission(self):
        allowed = super().permission()
        if allowed:
            viewkey = request.args.get('viewkey', None)
            if not viewkey:
                allowed = False
            else:
                race = SponsorRace.query.filter_by(viewkey=viewkey).one_or_none()
                if not race:
                    allowed = False
        return allowed

    def beforequery(self):
        viewkey = request.args.get('viewkey')
        race = SponsorRace.query.filter_by(viewkey=viewkey).one()
        self.queryparams.update({
            'race': race,
        })

sponsorview = ViewkeyView(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Sponsor,
                    roles_accepted = [],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Sponsorships View',
                    endpoint = 'admin.sponsorshipsview',
                    rule = '/sponsorshipsview',   # NOTE: need to change sponsorshipsview.js if this changes
                    dbmapping = sponsorview_dbmapping,
                    formmapping = sponsorview_formmapping,
                    clientcolumns = [
                        { 'data': 'raceyear', 'name': 'raceyear', 'label': 'Race Year',
                        },
                        { 'data': 'race', 'name': 'race', 'label': 'Race',
                        },
                        { 'data': 'client', 'name': 'client', 'label': 'Sponsor',
                        },
                        { 'data': 'client_name', 'name': 'client_name', 'label': 'Sponsor Name', 'type': 'readonly',
                        },
                        { 'data': 'client_email', 'name': 'client_email', 'label': 'Sponsor Email', 'type': 'readonly',
                        },
                        { 'data': 'state', 'name': 'state', 'label': 'State',
                        },
                        { 'data': 'level', 'name': 'level', 'label': 'Sponsorship Level',
                        },
                        { 'data': 'amount', 'name': 'amount', 'label': 'Amount',
                        },
                        { 'data': 'racecontact', 'name': 'racecontact', 'label': 'Race Contact',
                        },
                        { 'data': 'trend', 'name': 'trend', 'label': 'Trend', 'type':'readonly',
                        },
                        { 'data': 'notes', 'name': 'notes', 'label': 'Notes', 'type':'textarea',
                          'render': '$.fn.dataTable.render.ellipsis( 20 )',
                        },
                    ],
                    servercolumns = None,  # not server side
                    idSrc = 'rowid',
                    buttons = [
                               {
                                    'extend': 'csv',
                                    'text': 'CSV',
                                    'exportOptions': {
                                        'columns': ':gt(0)',    # skip first column
                                    }
                                }
                    ],
                    dtoptions = {
                                    'scrollCollapse': True,
                                    'scrollX': True,
                                    'scrollXInner': "100%",
                                    'scrollY': True,
                                    'lengthMenu': [ [-1, 10, 25, 50], ["All", 10, 25, 50] ],
                                    'fixedColumns': {
                                                      'leftColumns': 3,
                                                    },
                                  },
                    pretablehtml = sponsorview_filters.render(),
                    yadcfoptions = sponsorview_yadcf_options,
                    )
sponsorview.register()

##########################################################################################
# sponsorsummary endpoint
###########################################################################################

sponsorsummary_dbattrs = 'id,raceyear,racecontact,amount,trend,race,client,state,level,level.treatment,datesolicited,dateagreed,invoicesent'.split(',')
sponsorsummary_formfields = 'rowid,raceyear,racecontact,amount,trend,race,client,state,level,treatment,datesolicited,dateagreed,invoicesent'.split(',')
sponsorsummary_dbmapping = dict(list(zip(sponsorsummary_dbattrs, sponsorsummary_formfields)))
sponsorsummary_formmapping = dict(list(zip(sponsorsummary_formfields, sponsorsummary_dbattrs)))

## yadcf external filters
sponsorsummary_filters = '\n'.join([
            "<div class='external-filter filter-container'>",
            "    <div class='filter-item'>",
            "        <span class='label'>Race</span>",
            "        <span id='external-filter-race' class='filter'></span>",
            "    </div>",
            # the year filter is not handled by yadcf, check sponsor-summary.js
            "    <div class='filter-item'>",
            "        <span class='label'>Year</span>",
            "        <span id='summary-race-year' class='filter'></span>",
            "    </div>",
            "</div>",
            ])

## options for yadcf
sponsorsummary_yadcf_options = [
          {
           'column_selector': 'race.race:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '300px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select race', 
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-race',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
    ]

class SponsorSummary(DbCrudApiRolePermissions):
    def __init__(self, **kwargs):
        args = dict(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = Sponsor,
                    template = 'sponsor.summary.jinja2',
                    templateargs={'adminguide': adminguide},
                    dbmapping = sponsorsummary_dbmapping,
                    formmapping = sponsorsummary_formmapping,
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'raceyear', 'name': 'raceyear', 'label': 'Race Year',
                          'className': 'field_req',
                        },
                        { 'data': 'race', 'name': 'race', 'label': 'Race',
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorRace, 'labelfield':'race', 'formfield':'race',
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                           } },
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
                        },
                        { 'data': 'level', 'name': 'level', 'label': 'sponsorsummaryship Level',
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorLevel, 'labelfield':'race_level', 'formfield':'level',
                                                              'dbfield':'level', 'uselist':False, 'searchbox':True,
                           } }
                        },
                        { 'data': 'treatment', 'name': 'treatment', 'label': 'Treatment',
                          'className': 'field_req',
                        },
                        { 'data': 'amount', 'name': 'amount', 'label': 'Amount',
                          'className': 'field_req',
                        },
                        { 'data': 'trend', 'name': 'trend', 'label': 'Trend', 'type':'select2',
                          'className': 'field_req',
                          'options':['new','same','up','down','lost'],
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
                    ],
                    servercolumns = None,  # not server side
                    idSrc = 'rowid',
                    buttons = [],
                    dtoptions = {
                                    'scrollCollapse': True,
                                    'scrollX': True,
                                    'scrollXInner': "100%",
                                    'scrollY': True,
                                    'lengthMenu': [ [-1], ["All"] ],
                                    'fixedColumns': {
                                                      'leftColumns': 3,
                                                    },
                                    'drawCallback': { 'eval' : 'summary_drawcallback'  }
                                  },
        )
        args.update(kwargs)

        # this initialization needs to be done before checking any self.xxx attributes
        super().__init__(**args)

    def open(self):
        super().open()

        # flag any errors found after copying then resetting self.rows
        # NOTE: this assumes SponsorContract is instantiated as a client table (i.e., not serverside)
        theserows = list(self.rows)
        self.rows = iter(theserows)
        error_list = check_sponsorship_conflicts(theserows)
        if error_list:
            flash(render_sponsorship_conflicts(error_list))

sponsorsummary = SponsorSummary(
    roles_accepted=['super-admin', 'sponsor-admin'],
    pagename='Sponsorship Summary',
    endpoint='admin.sponsorsummary',
    rule='/sponsorsummary',
    pretablehtml=sponsorsummary_filters,
    yadcfoptions=sponsorsummary_yadcf_options,
)
sponsorsummary.register()

##########################################################################################
# sponsorsummaryview endpoint
##########################################################################################

## filters
sponsorsummaryview_filters = filtercontainerdiv()
with sponsorsummaryview_filters:
    # need loutilities-3.4 to call this as a function, hack below until url_for can be used
    # button('Details', url=url_for('admin.sponsorshipsview', id='sponsorsummary-details-button', style='margin-right:5px;'))
    button('Details', url='/admin/sponsorshipsview', id='sponsorsummary-details-button', style='margin-right:5px;')
    filterdiv('summary-race-year', 'Year')

class SponsorSummaryView(SponsorSummary, ViewkeyView):
    # SponsorSummary provides structure, ViewkeyView provides filtering on race
    pass

sponsorsummaryview_view = SponsorSummaryView (
    pagename='Sponsorship Summary View',
    endpoint='admin.sponsorsummaryview',
    rule='/sponsorsummaryview',
    pretablehtml=sponsorsummaryview_filters.render(),
)
sponsorsummaryview_view.register()

##########################################################################################
# sponsorraces endpoint
###########################################################################################

sponsorrace_dbattrs = 'id,race,raceshort,racedirector,rdphone,rdemail,isRDCertified,raceurl,sponsorurl,' \
                      'couponprovider,couponproviderid,description,display,viewkey,timezone,' \
                      'email_from,query_cc,agreement_cc'.split(',')
sponsorrace_formfields = 'rowid,race,raceshort,racedirector,rdphone,rdemail,isRDCertified,raceurl,sponsorurl,' \
                         'couponprovider,couponproviderid,description,display,viewkey,timezone,' \
                         'email_from,query_cc,agreement_cc'.split(',')
sponsorrace_dbmapping = dict(list(zip(sponsorrace_dbattrs, sponsorrace_formfields)))
sponsorrace_formmapping = dict(list(zip(sponsorrace_formfields, sponsorrace_dbattrs)))

def race_validate(action, formdata):
    results = []

    # regex patterns from http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
    for field in ['raceurl','sponsorurl']:
        if formdata[field] and not match(REGEX_URL, formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid url: correct format is like http[s]://example.com' })

    email_error = escape('invalid email: correct format is like john.doe@example.com or John Doe <john.doe@example.com>')
    for field in ['email_from']:
        if formdata[field] and not match(REGEX_EMAIL, formdata[field]):
            results.append({ 'name' : field, 'status' : email_error })

    for field in ['query_cc', 'agreement_cc']:
        if formdata[field]:
            addrs = formdata[field].split(';')
            for addr in addrs:
                if not match(REGEX_EMAIL, addr.strip()):
                    results.append({ 'name' : field, 'status' : email_error })
                    break

    return results

us_timezones = [t for t in all_timezones if t[0:3] == "US/"]

sponsorrace = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorRace, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
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
                        { 'data': 'email_from', 'name': 'email_from', 'label': 'Email From', 
                          'className': 'field_req',
                          'fieldInfo': 'from field for Race Services Query and Race Services Agreement',
                          # https://datatables.net/manual/data/renderers#Text-helper
                          'render': 'DataTable.render.text()',
                        },
                        { 'data': 'agreement_cc', 'name': 'agreement_cc', 'label': 'Agreement Email Cc',
                          'className': 'field_req',
                          'fieldInfo': 'cc field for Race Services Agreement<br/>enter email addresses separated by semicolon (";")'
                          '<br/>Director Email is automatically included',
                          'render': 'DataTable.render.text()',
                        # TODO: was unable to get this to work to add select values on the fly
                        #   'type': 'select2', 'separator': ';',
                        #   'opts': {'tags': True, 'multiple': True, 'tokenSeparators': [',', ' '], },
                        },
                        { 'data': 'query_cc', 'name': 'query_cc', 'label': 'Query Email Cc',
                          'className': 'field_req',
                          'fieldInfo': 'cc field for Race Services Query<br/>enter email addresses separated by semicolon (";")'
                          '<br/>Director Email is automatically included',
                          'render': 'DataTable.render.text()',
                        #   'type': 'select2', 'separator': ';',
                        #   'opts': {'tags': True, 'multiple': True, 'tokenSeparators': [',', ' '], },
                        },
                        {'data': 'timezone', 'name': 'timezone', 'label': 'Timezone',
                        'className': 'field_req',
                        'type': 'select2',
                        'options': us_timezones,
                        },
                         { 'data': 'couponprovider', 'name': 'couponprovider', 'label': 'Coupon Provider', 
                        },
                        { 'data': 'couponproviderid', 'name': 'couponproviderid', 'label': 'Coupon Provider ID', 
                        },
                        { 'data': 'viewkey', 'name': 'viewkey', 'label': 'View Key',
                          'render': lambda: {'eval': 'sponsorview_link( [["{}", "Details"], ["{}", "Summary"]] )'.format(
                              url_for('admin.sponsorshipsview'), url_for('admin.sponsorsummaryview'))},
                          },
                        { 'data': 'display', 'name': 'display', 'label': 'Display',
                          'className': 'field_req',
                          '_treatment' : {'boolean':{'formfield':'display', 'dbfield':'display'}},
                          'ed':{ 'def': 'yes' },
                        },
                        { 'data': 'description', 'name': 'description', 'label': 'Description',
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
                                        'fixedColumns': {
                                                          'leftColumns': 2,
                                                        },
                                  },
                    )
sponsorrace.register()

##########################################################################################
# sponsorlevels endpoint
###########################################################################################

sponsorlevel_dbattrs = 'id,race,level,minsponsorship,couponcount,maxallowed,treatment,description,display'.split(',')
sponsorlevel_formfields = 'rowid,race,level,minsponsorship,couponcount,maxallowed,treatment,description,display'.split(',')
sponsorlevel_dbmapping = dict(list(zip(sponsorlevel_dbattrs, sponsorlevel_formfields)))
sponsorlevel_formmapping = dict(list(zip(sponsorlevel_formfields, sponsorlevel_dbattrs)))

## yadcf external filters
sponsorlevel_filters = '\n'.join([
            "<div class='external-filter filter-container'>",
            "    <div class='filter-item'>",
            "        <span class='label'>Race</span>",
            "        <span id='external-filter-race' class='filter'></span>",
            "    </div>",
            "</div>",
            ])

## options for yadcf
sponsorlevel_yadcf_options = [
          {
           'column_selector': 'race.race:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '300px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select race', 
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-race',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
    ]

sponsorlevel = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorLevel, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
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
                        { 'data': 'treatment', 'name': 'treatment', 'label': 'Treatment', 'type': 'select2',
                          'className': 'field_req',
                          'options': ['summarize', 'not in summary'],
                          'ed': {'def': 'summarize'},
                          },
                        { 'data': 'description', 'name': 'description', 'label': 'Description for Agreement',
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
                                        'order': [['race.race:name', 'asc'], ['minsponsorship:name', 'desc']],
                                  },
                    pretablehtml = sponsorlevel_filters,
                    yadcfoptions = sponsorlevel_yadcf_options,
                    )
sponsorlevel.register()

##########################################################################################
# sponsorracedates endpoint
###########################################################################################

sponsorracedate_dbattrs = 'id,race,raceyear,racedate,beneficiary,raceloc'.split(',')
sponsorracedate_formfields = 'rowid,race,raceyear,racedate,beneficiary,raceloc'.split(',')
sponsorracedate_dbmapping = dict(list(zip(sponsorracedate_dbattrs, sponsorracedate_formfields)))
sponsorracedate_formmapping = dict(list(zip(sponsorracedate_formfields, sponsorracedate_dbattrs)))

sponsorracedate = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorRaceDate, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
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
                        { 'data': 'beneficiary', 'name': 'beneficiary', 'label': 'Beneficiary', 
                          'className': 'field_req',
                        },
                        { 'data': 'raceloc', 'name': 'raceloc', 'label': 'Race Location', 
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
                                        'order': [
                                          ['raceyear:name', 'desc'], 
                                          ['race.race:name', 'asc'], 
                                          ['racedate:name', 'desc']
                                        ],
                                  },
                    )
sponsorracedate.register()

##########################################################################################
# sponsorracevbls endpoint
###########################################################################################

def vbl_validate(action, formdata):
    results = []

    # regex patterns from http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
    for field in ['variable']:
        if formdata[field] and not match(REGEX_VBL, formdata[field]):
            results.append({ 'name' : field, 'status' : 'invalid variable: start with letter, then letters, digits, _ or $, no spaces ' })

    return results

sponsorracevbl_dbattrs = 'id,race,variable,value'.split(',')
sponsorracevbl_formfields = 'rowid,race,variable,value'.split(',')
sponsorracevbl_dbmapping = dict(list(zip(sponsorracevbl_dbattrs, sponsorracevbl_formfields)))
sponsorracevbl_formmapping = dict(list(zip(sponsorracevbl_formfields, sponsorracevbl_dbattrs)))

## yadcf external filters
sponsorracevbl_filters = '\n'.join([
            "<div class='external-filter filter-container'>",
            "    <div class='filter-item'>",
            "        <span class='label'>Race</span>",
            "        <span id='external-filter-race' class='filter'></span>",
            "    </div>",
            "</div>",
            ])

## options for yadcf
sponsorracevbl_yadcf_options = [
          {
           'column_selector': 'race.race:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '300px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select race', 
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-race',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
    ]

sponsorracevbl = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorRaceVbl, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Sponsor Race Variables', 
                    endpoint = 'admin.sponsorracevbls', 
                    rule = '/sponsorracevbls', 
                    dbmapping = sponsorracevbl_dbmapping, 
                    formmapping = sponsorracevbl_formmapping, 
                    checkrequired = True,
                    validate = vbl_validate,
                    clientcolumns = [
                        { 'data': 'race', 'name': 'race', 'label': 'Race',
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorRace, 'labelfield':'race', 'formfield':'race', 
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                           } }
                        },
                        { 'data': 'variable', 'name': 'variable', 'label': 'Variable', 
                          'className': 'field_req',
                        },
                        { 'data': 'value', 'name': 'value', 'label': 'Value', 
                          'className': 'field_req',
                        },
                    ], 
                    servercolumns = None,  # not server side
                    idSrc = 'rowid', 
                    buttons = ['create', 'editRefresh', 'remove', 'csv'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                        'order': [['race.race:name', 'asc'], ['variable:name', 'asc']],
                                  },
                    pretablehtml = sponsorracevbl_filters,
                    yadcfoptions = sponsorracevbl_yadcf_options,
                    )
sponsorracevbl.register()

##########################################################################################
# sponsorbenefits endpoint
###########################################################################################

sponsorbenefit_dbattrs = 'id,race,order,benefit,description,levels'.split(',')
sponsorbenefit_formfields = 'rowid,race,order,benefit,description,levels'.split(',')
sponsorbenefit_dbmapping = dict(list(zip(sponsorbenefit_dbattrs, sponsorbenefit_formfields)))
sponsorbenefit_formmapping = dict(list(zip(sponsorbenefit_formfields, sponsorbenefit_dbattrs)))

## yadcf external filters
sponsorbenefit_filters = '\n'.join([
            "<div class='external-filter filter-container'>",
            "    <div class='filter-item'>",
            "        <span class='label'>Race</span>",
            "        <span id='external-filter-race' class='filter'></span>",
            "    </div>",
            "</div>",
            ])

## options for yadcf
sponsorbenefit_yadcf_options = [
          {
           'column_selector': 'race.race:name',
            'select_type': 'select2',
            'select_type_options': {
                'width': '300px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id' : -1,
                    'text': 'Select race', 
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-race',
            'filter_reset_button_text': False, # hide yadcf reset button
          },
    ]

sponsorbenefit = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorBenefit, 
                    version_id_col = 'version_id',  # optimistic concurrency control
                    roles_accepted = ['super-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Sponsor Benefits', 
                    endpoint = 'admin.sponsorbenefits', 
                    rule = '/sponsorbenefits', 
                    dbmapping = sponsorbenefit_dbmapping, 
                    formmapping = sponsorbenefit_formmapping, 
                    checkrequired = True,
                    clientcolumns = [
                        { 'data': 'race', 'name': 'race', 'label': 'Race', 
                          'className': 'field_req',
                          '_treatment' : { 'relationship' : { 'fieldmodel':SponsorRace, 'labelfield':'race', 'formfield':'race', 
                                                              'dbfield':'race', 'uselist':False, 'searchbox':True,
                           } },
                           '_update' : {'options': 
                                DteDbDependent(
                                               model=SponsorRace, 
                                               modelfield='id',
                                               depmodel=SponsorLevel, 
                                               depmodelref='race_id',
                                               depmodelfield='race_level', 
                                               depformfield='levels.id', # <dependentfield>.<relationship valuefield, default 'id'>
                                               depvaluefield='id', 
                                               )
                           },
                        },
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
                    buttons = ['create', 'editRefresh', 'remove', 'csv'],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'lengthMenu': [ [-1, 10, 25, 50], ["All", 10, 25, 50] ],
                                        'scrollY': True,
                                        'order': [['race.race:name', 'asc'], ['order:name', 'asc']],
                                  },
                    pretablehtml = sponsorbenefit_filters,
                    yadcfoptions = sponsorbenefit_yadcf_options,
                    )
sponsorbenefit.register()

##########################################################################################
# sponsorquerylogs endpoint
###########################################################################################

sponsorquerylog_dbattrs = 'id,time,organization,name,phone,city,state,street,zipcode,email,race,amount,level,comments'.split(',')
sponsorquerylog_formfields = 'rowid,time,organization,name,phone,city,state,street,zipcode,email,race,amount,level,comments'.split(',')
sponsorquerylog_dbmapping = dict(list(zip(sponsorquerylog_dbattrs, sponsorquerylog_formfields)))
sponsorquerylog_formmapping = dict(list(zip(sponsorquerylog_formfields, sponsorquerylog_dbattrs)))

sponsorquerylog = DbCrudApiRolePermissions(
                    app = bp,   # use blueprint instead of app
                    db = db,
                    model = SponsorQueryLog, 
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'datatables.jinja2',
                    templateargs={'adminguide': adminguide},
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
                                'editRefresh',
                                'csv',
                    ],
                    dtoptions = {
                                        'scrollCollapse': True,
                                        'scrollX': True,
                                        'scrollXInner': "100%",
                                        'scrollY': True,
                                        'order': [['time:name', 'desc']],
                                  },
                    )
sponsorquerylog.register()

