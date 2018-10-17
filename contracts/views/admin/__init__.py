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

bp = Blueprint('admin', __name__.split('.')[0], url_prefix='/admin')

# import views
import login
import userrole
import events
import contractviews
import sysinfo