"""blueprint for this view folder
"""

from flask import Blueprint

bp = Blueprint('admin', __name__.split('.')[0], url_prefix='/admin', static_folder='static/admin', template_folder='templates/admin')

# import views
from . import common
from . import events
from . import admin_eventscalendar
from . import tags
from . import daterules
from . import contractviews
from . import sponsors
from . import racessummary
from . import sysinfo