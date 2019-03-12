###########################################################################################
# blueprint for this view folder
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/21/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################

from flask import Blueprint

bp = Blueprint('admin', __name__.split('.')[0], url_prefix='/admin', static_folder='static/admin', template_folder='templates/admin')

# import views
import login
import userrole
import events
import admin_eventscalendar
import tags
import daterules
import contractviews
import sponsors
import sysinfo