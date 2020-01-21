###########################################################################################
# racessummary - summary views for races
#
#       Date            Author          Reason
#       ----            ------          ------
#       05/17/19        Lou King        Create
#
#   Copyright 2019 Lou King
#
###########################################################################################
'''
racessummary - summary views for races
====================================================
'''
# standard
from csv import DictWriter
from tempfile import TemporaryFile

# pypi
from flask import current_app, jsonify
from flask.views import MethodView

# homegrown
from . import bp
from contracts.dbmodel import SponsorRace
from contracts.runsignup import RunSignUp
from loutilities.timeu import asctime
from loutilities.tables import CrudApi

# convert mm/dd/yyyy hh:mm to yyyy-mm-dd
ymd = asctime('%Y-%m-%d')
mdy = asctime('%m/%d/%Y')
getdate = lambda d: ymd.dt2asc(mdy.asc2dt(d.split(' ')[0]))

debug = False

##########################################################################################
class RaceSummaryApi(CrudApi):
##########################################################################################

    from flask_security import current_user

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
    #----------------------------------------------------------------------
        if debug: current_app.logger.debug('RaceSummaryApi.__init__()')

        # the args dict has default values for arguments added by this derived class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(roles_accepted=None, roles_required=None)
        args.update(kwargs)

        # this initialization needs to be done before checking any self.xxx attributes
        super(RaceSummaryApi, self).__init__(**args)

        # Caller should use roles_accepted OR roles_required but not both
        if self.roles_accepted and self.roles_required:
            raise parameterError('use roles_accepted OR roles_required but not both')

        # assure None or [ 'role1', ... ]
        if self.roles_accepted and not isinstance(self.roles_accepted, list):
            self.roles_accepted = [ self.roles_accepted ]
        if self.roles_required and not isinstance(self.roles_required, list):
            self.roles_required = [ self.roles_required ]

    # ----------------------------------------------------------------------
    def permission(self):
    # ----------------------------------------------------------------------
        '''
        determine if current user is permitted to use the view
        '''
        if debug: current_app.logger.debug('DbCrudApiRolePermissions.permission()')
        if debug: current_app.logger.debug(
            'permission: roles_accepted = {} roles_required = {}'.format(self.roles_accepted, self.roles_required))
    
        # if no roles are asked for, permission granted
        if not self.roles_accepted and not self.roles_required:
            allowed = True
    
        # if user has any of the roles_accepted, permission granted
        elif self.roles_accepted:
            allowed = False
            for role in self.roles_accepted:
                if self.current_user.has_role(role):
                    allowed = True
                    break
    
        # if user has all of the roles_required, permission granted
        elif self.roles_required:
            allowed = True
            for role in self.roles_required:
                if not self.current_user.has_role(role):
                    allowed = False
                    break
    
        return allowed

    #-------------------------------------------------------------------------------------
    def open(self):
    #-------------------------------------------------------------------------------------
        races = SponsorRace.query.filter_by(display=True).all()

        with RunSignUp(key=current_app.config['RSU_KEY'], secret=current_app.config['RSU_SECRET']) as rsu:
            racedata = {}
            for race in races:
                # skip races for which we have no api
                if race.couponprovider != 'RunSignUp' or not race.couponproviderid: continue

                if race.race not in racedata:
                    thisrace = race.race
                    racedata[thisrace] = {}

                events = rsu.getraceevents(race.couponproviderid)

                for event in events:
                    racedate = getdate(event['start_time'])
                    thisevent = event['name']
                    if thisevent not in racedata[thisrace]:
                        racedata[thisrace][thisevent] = {'event_id': event['event_id'], 'dates': {}}
                    if racedate not in racedata[thisrace][thisevent]['dates']:
                        racedata[thisrace][thisevent]['dates'][racedate] = {'regcounts': {}}
                        if event['registration_opens']:
                            racedata[thisrace][thisevent]['dates'][racedate]['regopendate'] = getdate(event['registration_opens'])

                    participants = rsu.getraceparticipants(race.couponproviderid, event['event_id'])

                    for participant in participants:
                        regdate = getdate(participant['registration_date'])
                        if regdate not in racedata[thisrace][thisevent]['dates'][racedate]['regcounts']:
                            racedata[thisrace][thisevent]['dates'][racedate]['regcounts'][regdate] = 0
                        racedata[thisrace][thisevent]['dates'][racedate]['regcounts'][regdate] += 1

            # build response
            self.response = []

            for thisrace in racedata:
                for thisevent in racedata[thisrace]:
                    for racedate in racedata[thisrace][thisevent]['dates']:
                        # we know the registration date
                        if 'regopendate' in racedata[thisrace][thisevent]['dates'][racedate]:
                            regopendate = racedata[thisrace][thisevent]['dates'][racedate]['regopendate']
                        # we have to guess at registration open, as the lowest date
                        else:
                            regopendate = min([regdate for regdate in racedata[thisrace][thisevent]['dates'][racedate]['regcounts']])
                        for regdate in racedata[thisrace][thisevent]['dates'][racedate]['regcounts']:
                            count = racedata[thisrace][thisevent]['dates'][racedate]['regcounts'][regdate]
                            self.response.append(
                                {'race': thisrace,
                                 'event': thisevent,
                                 'regopen_date': regopendate,
                                 'registration_date': regdate,
                                 'race_date': racedate,
                                 'count': count,
                                 }
                            )

    #-------------------------------------------------------------------------------------
    def nexttablerow(self):
    #-------------------------------------------------------------------------------------
        if len(self.response) > 0:
            return self.response.pop(0)
        else:
            raise StopIteration

    # -------------------------------------------------------------------------------------
    def close(self):
    # -------------------------------------------------------------------------------------
        pass

##########################################################################################
# racesummary endpoint
###########################################################################################

## yadcf external filters
racesummary_filters = '\n'.join([
            "<div class='external-filter filter-container'>",
            "    <div class='filter-item'>",
            "        <span class='label'>Race</span>",
            "        <span id='external-filter-race' class='filter'></span>",
            "    </div>",
            "    <div class='filter-item'>",
            "        <span class='label'>Event</span>",
            "        <span id='external-filter-events' class='filter'></span>",
            "    </div>",
            # the charttype filter is not handled by yadcf, check race-summary.js
            "    <div class='filter-item'>",
            "        <span class='label'>Chart Type</span>",
            "        <span id='summary-race-charttype' class='filter'></span>",
            "    </div>",
            # the numyears filter is not handled by yadcf, check race-summary.js
            "    <div class='filter-item'>",
            "        <span class='label'>Num Years</span>",
            "        <span id='summary-race-numyears' class='filter'></span>",
            "    </div>",
            "</div>",
            ])

## options for yadcf
racecol = 1
eventcol = 3
racesummary_yadcf_options = {
    'columns' : [
        {
            'column_number': racecol,
            'select_type': 'select2',
            'select_type_options': {
                'width': '300px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id': -1,
                    'text': 'Select race',
                },
            },
            'filter_type': 'select',
            'filter_container_id': 'external-filter-race',
            'filter_reset_button_text': False,  # hide yadcf reset button
        },
        {
            'column_number': eventcol,
            'select_type': 'select2',
            'select_type_options': {
                'width': '200px',
                'allowClear': True,  # show 'x' (remove) next to selection inside the select itself
                'placeholder': {
                    'id': -1,
                    'text': 'Select events',
                },
            },
            'filter_type': 'multi_select',
            'filter_container_id': 'external-filter-events',
            'filter_match_mode': 'exact',
            'column_data_type': 'text',
            'text_data_delimiter': ', ',
            'filter_reset_button_text': False,  # hide yadcf reset button
        },
    ],
}

racesummary = RaceSummaryApi(
                    app = bp,   # use blueprint instead of app
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'race.summary.jinja2',
                    pagename = 'Race Summary',
                    endpoint = 'admin.racesummary',
                    rule = '/racesummary',
                    clientcolumns = [
                        { 'data': 'race', 'name': 'race', 'label': 'Race',
                        },
                        { 'data': 'race_date', 'name': 'race_date', 'label': 'Race Date',
                        },
                        { 'data': 'event', 'name': 'event', 'label': 'Event',
                        },
                        { 'data': 'registration_date', 'name': 'registration_date', 'label': 'Registration Date',
                        },
                        { 'data': 'count', 'name': 'count', 'label': 'Count',
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
                        'order': [[1, 'asc'], [2, 'asc'], [3, 'asc'], [4, 'asc']],
                        'lengthMenu': [[-1], ["All"]],
                        'drawCallback': {'eval': 'racesummary_drawcallback'}
                    },
                    pretablehtml = racesummary_filters,
                    yadcfoptions = racesummary_yadcf_options,
                    )
racesummary.register()