'''
racessummary - summary views for races
====================================================
'''
# standard

# pypi
from flask import current_app, request
from loutilities.timeu import asctime
from loutilities.tables import CrudApi
from dominate.tags import div, h2
from loutilities.filters import filtercontainerdiv, filterdiv, yadcfoption

# homegrown
from . import bp
from ...dbmodel import db, SponsorRace, SponsorRaceRegCache
from ...caching import update_raceregcache
from ...version import __docversion__

adminguide = f'https://contractility.readthedocs.io/en/{__docversion__}/contract-admin-sponsor-guide.html'

# convert mm/dd/yyyy hh:mm to yyyy-mm-dd
ymd = asctime('%Y-%m-%d')
mdy = asctime('%m/%d/%Y')
getdate = lambda d: ymd.dt2asc(mdy.asc2dt(d.split(' ')[0]))

debug = False
class parameterError(Exception): pass

class RaceRegistrationsApi(CrudApi):

    from flask_security import current_user

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
    #----------------------------------------------------------------------
        if debug: current_app.logger.debug('RaceRegistrationsApi.__init__()')

        # the args dict has default values for arguments added by this derived class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(roles_accepted=None, roles_required=None)
        args.update(kwargs)

        # this initialization needs to be done before checking any self.xxx attributes
        super(RaceRegistrationsApi, self).__init__(**args)

        # Caller should use roles_accepted OR roles_required but not both
        if self.roles_accepted and self.roles_required:
            raise parameterError('use roles_accepted OR roles_required but not both')

        # assure None or [ 'role1', ... ]
        if self.roles_accepted and not isinstance(self.roles_accepted, list):
            self.roles_accepted = [ self.roles_accepted ]
        if self.roles_required and not isinstance(self.roles_required, list):
            self.roles_required = [ self.roles_required ]

    def permission(self):
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

    def open(self):
        race_id = request.args.get('race', None)
        race = SponsorRace.query.filter_by(id=race_id, display=True).one_or_none()

        # skip races for which we have no api
        if race.couponprovider != 'RunSignUp' or not race.couponproviderid: 
            raise f'invalid race_id {race_id} received'

        racedata = {}
        
        if race.race not in racedata:
            thisrace = race.race
            racedata[thisrace] = {}

        try:
            events = update_raceregcache(race.couponproviderid)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        for event in events:
            # race date is date of event start, unless end time is specified
            racedate = getdate(event['start_time'])
            if event['end_time']:
                racedate = getdate(event['end_time'])
            thisevent = event['name']
            if thisevent not in racedata[thisrace]:
                racedata[thisrace][thisevent] = {'event_id': event['event_id'], 'dates': {}}
            if racedate not in racedata[thisrace][thisevent]['dates']:
                racedata[thisrace][thisevent]['dates'][racedate] = {'regcounts': {}}
                if event['registration_opens']:
                    racedata[thisrace][thisevent]['dates'][racedate]['regopendate'] = getdate(event['registration_opens'])

            participants = SponsorRaceRegCache.query.filter_by(event_id=event['event_id']).all()

            for participant in participants:
                regdate = ymd.dt2asc(participant.registration_date)
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

    def nexttablerow(self):
        if len(self.response) > 0:
            return self.response.pop(0)
        else:
            raise StopIteration

    def close(self):
        pass

##########################################################################################
# raceregistrations endpoint
###########################################################################################

## yadcf external filters
def raceregistrations_pretablehtml():
    race_id = request.args.get('race')
    race = SponsorRace.query.filter_by(id=race_id, display=True).one()
    pretablehtml = div()
    with pretablehtml:
        h2(race.race)
        raceregistrations_filters = filtercontainerdiv()
        with raceregistrations_filters:
            filterdiv('external-filter-events', 'Events')
            filterdiv('summary-race-charttype', 'Chart Type')
            filterdiv('summary-race-numyears', 'Num Years')
    return pretablehtml.render()

## options for yadcf
raceregistrations_yadcf_options = {
    'columns' : [
        {
            'column_selector': 'race:name',
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
            'column_selector': 'event:name',
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

raceregistrations_view = RaceRegistrationsApi(
                    app = bp,   # use blueprint instead of app
                    roles_accepted = ['super-admin', 'sponsor-admin'],
                    template = 'race.summary.jinja2',
                    templateargs={'adminguide': adminguide},
                    pagename = 'Race Registrations',
                    endpoint = 'admin.raceregistrations',
                    rule = '/raceregistrations',
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
                        'order': [
                            ['race:name', 'asc'], 
                            ['race_date:name', 'asc'], 
                            ['event:name', 'asc'], 
                            ['registration_date:name', 'asc']
                        ],
                        'lengthMenu': [[-1], ["All"]],
                        'drawCallback': {'eval': 'raceregistrations_drawcallback'}
                    },
                    pretablehtml = raceregistrations_pretablehtml,
                    yadcfoptions = raceregistrations_yadcf_options,
                    )
raceregistrations_view.register()