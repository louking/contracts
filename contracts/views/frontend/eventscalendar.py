###########################################################################################
# calendar - events api for contracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/08/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
calendar - events api for contracts database
=======================================================================

Supports API for fullcalendar javascript client
'''

# pypi
from flask import request, jsonify, render_template, url_for
from flask.views import MethodView

# home grown
from . import bp
from contracts.dbmodel import db, Event
from loutilities.flask_helpers.blueprints import add_url_rules

class parameterError(Exception): pass

# jquery ui theme
jqueryui_cdn = 'https://code.jquery.com'
jqueryui_ver = '1.12.1'

# fullcalendar.js (see https://fullcalendar.io)
fullcalendar_cdn = 'https://cdnjs.cloudflare.com/ajax/libs'
fullcalendar_ver = '3.9.0'

calendar_scripts_js = [
    # calendar handling - see https://fullcalendar.io/download
    ('fullcalendar/{ver}/fullcalendar{min}.js', fullcalendar_ver, fullcalendar_cdn),
    'frontend/eventscalendar.js',
]
calendar_scripts_css = [
    ('fullcalendar/{ver}/fullcalendar{min}.css', fullcalendar_ver, fullcalendar_cdn),
    # this causes rendering problems. See https://stackoverflow.com/questions/25681573/fullcalendar-header-buttons-missing
    # ('fullcalendar/{ver}/fullcalendar.print.css', fullcalendar_ver, fullcalendar_cdn),
    ('ui/{ver}/themes/cupertino/jquery-ui.css', jqueryui_ver, jqueryui_cdn),
    'frontend_style.css',
    'frontend/eventscalendar.css',
]

#----------------------------------------------------------------------
def time24(time):
#----------------------------------------------------------------------
    # handle case of no time supplied
    if not time: return '00:00'

    # split out ampm (see events.py datetime format 'h:mm a')
    thetime, ampm = time.split(' ')

    # split time into fields h:m[:s]
    fields = [int(t) for t in thetime.split(':')]

    # hopefully this error was detected before time was put into database
    if len(fields) < 2 or len(fields) > 3:
        raise parameterError, 'invalid time field {} detected'.format(time)
    
    # use 24 hour clock
    if ampm.lower() == 'pm':
        fields[0] += 12
    
    # build and return string hh:mm[:ss]
    fieldstrs = []
    for field in fields:
        fieldstrs.append(str(field).zfill(2))
    return ':'.join(fieldstrs)

#######################################################################
class EventsCalendarApi(MethodView):
#######################################################################
    url_rules = {
                'eventsapi': ['/eventsapi',('GET',)],
                }

    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        # get start and end dates from arguments
        start = request.args.get( 'start' )
        end   = request.args.get( 'end' )

        # if arguments are insufficent, raise exception
        if not start or not end:
            raise parameterError, 'EventsCalendarApi: missing argument'

        # retrieve events between start and end dates
        events = Event.query.filter( Event.date >= start, Event.date <= end ).all()

        # build Event Objects per https://fullcalendar.io/docs/event-object
        eventobjects = []
        for event in events:
            # don't supply trivial events
            if len(event.services) == 0: continue
            # don't supply events which are only premium promotion
            if len(event.services) == 1 and event.services[0].service == 'premiumpromotion': continue

            # send event to client
            eventobject = {
                'id'    : event.id,
                'title' : event.event,
                'state' : event.state.state,
                'start' : event.date + 'T' + time24(event.mainStartTime),
            }
            eventobjects.append( eventobject )

        # and back to caller
        return jsonify( eventobjects )

#----------------------------------------------------------------------
add_url_rules(bp, EventsCalendarApi)
#----------------------------------------------------------------------

#######################################################################
class EventsCalendar(MethodView):
#######################################################################
    url_rules = {
                'calendar': ['/calendar',('GET',)],
                }

    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        from contracts.request import annotatescripts

        context = {
                   'pagename'          : 'events calendar',
                   'pagejsfiles'       : annotatescripts( calendar_scripts_js ),
                   'pagecssfiles'      : annotatescripts( calendar_scripts_css ),
                   'servicesqueryurl'  : request.url_root[0:-1] + url_for('.servicesquery')
                  }
        return render_template( 'frontend/eventscalendar.jinja2', **context )

#----------------------------------------------------------------------
add_url_rules(bp, EventsCalendar)
#----------------------------------------------------------------------


#######################################################################
class ServicesQuery(MethodView):
#######################################################################
    url_rules = {
                'servicesquery': ['/servicesquery',('GET',)],
                }

    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        from contracts.request import annotatescripts

        context = {
                   'pagename'          : 'request race services',
                  }
        return render_template( 'frontend/servicesquery.jinja2', **context )

#----------------------------------------------------------------------
add_url_rules(bp, ServicesQuery)
#----------------------------------------------------------------------
