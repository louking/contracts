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
from contracts.dbmodel import db, Event, EventAvailabilityException, DateRule
from contracts.daterule import daterule2dates
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
class EventsExceptionsApi(MethodView):
#######################################################################
    url_rules = {
                'eventexceptionsapi': ['/eventexceptionsapi',('GET',)],
                }

    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        # get start and end dates from arguments
        start = request.args.get( 'start' ) # yyyy-mm-dd
        end   = request.args.get( 'end' )   # yyyy-mm-dd

        # if arguments are insufficent, raise exception
        if not start or not end:
            raise parameterError, 'EventsExceptionsApi: missing argument'

        # determine start and end year
        startyear = int( start.split('-')[0] )
        endyear   = int( end.split('-')[0] )

        # determine start and end months
        # dates are yyyy-mm-dd where mm is one based
        month_start_ndx = int( start.split('-')[1] ) - 1
        month_end_ndx   = int( end.split('-')[1] ) - 1

        # retrieve events between start and end dates
        exceptions = []
        month_db  = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # keep track of year which each month belongs to
        monyear = {}

        # if the same year, pull in start month through end month
        if startyear == endyear:
            for mon in month_db[ month_start_ndx : month_end_ndx+1 ]:
                exceptions += (EventAvailabilityException.query
                                .filter( EventAvailabilityException.daterule_id==DateRule.id )
                                .filter( DateRule.month==mon )
                                .all())
                monyear[mon] = startyear

        # if the end year is the year following the start year
        elif startyear + 1 == endyear:
            # use end of year, then start of year
            for mon in month_db[ month_start_ndx : ]:
                exceptions += (EventAvailabilityException.query
                                .filter( EventAvailabilityException.daterule_id==DateRule.id )
                                .filter( DateRule.month==mon )
                                .all())
                monyear[mon] = startyear
            for mon in month_db[ : month_end_ndx]:
                exceptions += (EventAvailabilityException.query
                                .filter( EventAvailabilityException.daterule_id==DateRule.id )
                                .filter( DateRule.month==mon )
                                .all())
                monyear[mon] = endyear

        # this should not happen
        else:
            raise parameterError, 'invalid start / end combination: start={} end={}'.format(start, end)

        # Easter doesn't have a month to filter on
        # because we're lazy, just include it to get filtered out later if necessary
        exceptions += (EventAvailabilityException.query
                                .filter( EventAvailabilityException.daterule_id==DateRule.id )
                                .filter( DateRule.rule=='Easter' )
                                .all())

        # build list of eventobjects by going through event exceptions
        eventobjects = []
        for exception in exceptions:
            # all rules except Easter have a year
            if exception.daterule.rule != 'Easter':
                dates = daterule2dates(exception.daterule, monyear[exception.daterule.month])
            
            else:
                # handle Easter by determining month easter occurs in start year and end year
                # this will get filtered out later
                dates = daterule2dates(exception.daterule, startyear)
                if startyear != endyear:
                    dates += daterule2dates(exception.daterule, endyear)

            # scan the dates we've come up with for this exception, and include eventobject if within range
            for date in dates:
                # only return dates within the indicated range
                if date >= start and date <= end:
                    eventobject = {
                        'id'        : 'exc-{}'.format(exception.daterule.id),
                        'title'     : exception.shortDescr,
                        'start'     : date,
                        'exception' : exception.exception
                    }
                    eventobjects.append( eventobject )

        # and back to caller
        return jsonify( eventobjects )

#----------------------------------------------------------------------
add_url_rules(bp, EventsExceptionsApi)
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
        return render_template( 'eventscalendar.jinja2', **context )

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
        return render_template( 'servicesquery.jinja2', **context )

#----------------------------------------------------------------------
add_url_rules(bp, ServicesQuery)
#----------------------------------------------------------------------
