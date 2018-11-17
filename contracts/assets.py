###########################################################################################
# assets - javascript and css asset handling
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/16/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
#
###########################################################################################

'''
assets - javascript and css asset handling
===================================================
'''

from flask import current_app
from flask_assets import Environment, Bundle

bundles = {

    'frontend_js': Bundle(
        'js/lib/jquery-1.10.2.js',
        'js/home.js',
        output='gen/frontend.js',
        ),

    'frontend_css': Bundle(
        output='gen/frontend.css',
        ),

    'admin_js': Bundle(
        # Editor is not yet available from the dataTables CDN
        'js/Editor-1.8.0/js/dataTables.editor.js',
        'js/Editor-1.8.0/js/editor.jqueryui.js',
        'js/Editor-1.8.0/css/editor.jqueryui.css',

        'layout.js',
        output='gen/admin.js',
        ),

    'admin_css': Bundle(
        'js/jquery-ui-1.12.1.custom/jquery-ui{min}.js',
        'js/jquery-ui-1.12.1.custom/jquery-ui{min}.css', 
        'js/jquery-ui-1.12.1.custom/jquery-ui.structure{min}.css', 
        'js/jquery-ui-1.12.1.custom/jquery-ui.theme{min}.css', 
        'style.css',

        output='gen/admin.css',
        )
}

assets = Environment(current_app)

assets.register(bundles)
