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
from . import login
from . import common
from . import events
from . import admin_eventscalendar
from . import tags
from . import daterules
from . import contractviews
from . import sponsors
from . import racessummary
from . import sysinfo