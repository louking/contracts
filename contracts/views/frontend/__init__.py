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

# create blueprint first
bp = Blueprint('frontend', __name__.split('.')[0], url_prefix='', static_folder='static/frontend', template_folder='templates/frontend')

# import views
from . import frontend
from . import contractviews
from . import eventscalendar
from . import frontend_sponsors