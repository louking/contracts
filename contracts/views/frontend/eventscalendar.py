###########################################################################################
# calendar - frontend events api for contracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/08/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
calendar - frontend events api for contracts database
=======================================================================

Supports API for fullcalendar javascript client
'''

# pypi
from flask import current_app, request, jsonify, render_template, url_for
from flask.views import MethodView

# home grown
from . import bp
from contracts.dbmodel import db, Event, EventAvailabilityException, DateRule
from contracts.daterule import daterule2dates
from contracts.utils import time24
from contracts.mailer import sendmail
from loutilities.flask_helpers.blueprints import add_url_rules

class parameterError(Exception): pass

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
            # don't supply events which have been canceled
            if event.state.state == 'canceled': continue

            # send event to client
            eventobject = {
                'id'    : event.id,
                'title' : event.race.race,
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
        context = {
                   'pagename'          : 'events calendar',
                   # 'servicesqueryurl'  : request.url_root[0:-1] + url_for('.events-servicesquery')
                   'servicesqueryurl'  : url_for('.events-servicesquery')
                  }
        return render_template( 'eventscalendar.jinja2', **context )

#----------------------------------------------------------------------
add_url_rules(bp, EventsCalendar)
#----------------------------------------------------------------------


#######################################################################
class ServicesQuery(MethodView):
#######################################################################
    url_rules = {
                'events-servicesquery': ['/eventsservicesquery',('GET','POST',)],
                }

    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        context = {
                   'pagename'         : 'request race services',
                   'pageassets_css'   : 'materialize-css',
                   'pageassets_js'    : 'page-events-servicesquery-js',
                   'servicesqueryurl' : url_for( '.events-servicesquery' ),
                   'servicesquery_contact' : current_app.config['SERVICEQUERY_CONTACT'],
                  }
        return render_template( 'events-servicesquery.jinja2', **context )

    #----------------------------------------------------------------------
    def post(self):
    #----------------------------------------------------------------------
        # request.form is werkzeug.datastructures.ImmutableMultiDict
        # and each field will show up as list if we don't convert to dict here
        form = {k:v for k,v in request.form.items()}

        # process a couple of form entries for easier reading
        theseservices = []
        for service in ['is_finish_line', 'is_course_marking', 'is_premium_promotion']:
            if form.get(service, False):
                # skip 'is_' portion
                theseservices.append(service[3:])
        services = ', '.join(theseservices)
        form['services'] = services
        form['is_new_race'] = 'yes' if form.get('is_new_race', False) else 'no'

        # turn form into email
        html = render_template( 'events-servicesquery-mail.jinja2', **form)

        # TODO: this should be in database
        subject = '[FSRC-RACE-REQUEST] {}'.format(form['subject'])
        tolist = current_app.config['SERVICEQUERY_TO']
        # TODO: these should be in database
        cclist = current_app.config['SERVICEQUERY_CC'] + ['{} <{}>'.format(form['contact_name'], form['contact_email'])]
        fromlist = current_app.config['SERVICEQUERY_CONTACT']
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        context = {
                   'pagename'         : 'request race services - success',
                   'pageassets_css'   : 'materialize-css',
                   'pageassets_js'    : 'materialize-js',
                   'servicesquery_contact' : current_app.config['SERVICEQUERY_CONTACT'],
                  }
        return render_template( 'events-servicesquery-success.jinja2', **context )

#----------------------------------------------------------------------
add_url_rules(bp, ServicesQuery)
#----------------------------------------------------------------------
