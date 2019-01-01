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
from flask_assets import Bundle, Environment

# jquery
jq_ver = '3.3.1'
jq_ui_ver = '1.12.1'

# dataTables
dt_datatables_ver = '1.10.18'
dt_editor_ver = '1.8.1'
dt_buttons_ver = '1.5.4'
dt_colvis_ver = '1.5.4'
dt_fixedcolumns_ver = '3.2.5'
dt_select_ver = '1.2.6'
dt_editor_plugin_fieldtype_ver = '?'

# select2
# NOTE: patch to jquery ui required, see https://github.com/select2/select2/issues/1246#issuecomment-17428249
# currently in datatables.js
s2_ver = '4.0.5'

# yadcf
yadcf_ver = '0.9.3'

moment_ver = '2.22.2'       # moment.js (see https://momentjs.com/)
lodash_ver = '4.17.11'      # lodash.js (see https://lodash.com)
fullcalendar_ver = '3.9.0'  # fullcalendar.io
materialize_ver = '1.0.0'   # materializecss.com

materialize_bundle_js = Bundle(
        'js/materialize-v{ver}/materialize/js/materialize.js'.format(ver=materialize_ver),

        filters='jsmin',
        output='gen/materialize.js',
        )
materialize_bundle_css = Bundle(
        'js/materialize-v{ver}/materialize/css/materialize.css'.format(ver=materialize_ver),
        'materialize-override.css',

        filters=['cssrewrite', 'cssmin'],
        output='gen/materialize.css',
        )

asset_bundles = {

    'frontend_js': Bundle(
        'js/jQuery-{ver}/jquery-{ver}.js'.format(ver=jq_ver),
        'js/jquery-ui-{ver}.custom/jquery-ui.js'.format(ver=jq_ui_ver),

        # date time formatting 
        'js/moment-{ver}/moment.js'.format(ver=moment_ver),

        'js/fullcalendar-{ver}/fullcalendar.js'.format(ver=fullcalendar_ver),
        'legend.js',
        'frontend/eventscalendar.js',

        filters='jsmin',
        output='gen/frontend.js',
        ),

    'frontend_css': Bundle(
        'js/jquery-ui-{ver}.custom/jquery-ui.css'.format(ver=jq_ui_ver),
        'js/jquery-ui-{ver}.custom/jquery-ui.structure.css'.format(ver=jq_ui_ver),
        'js/jquery-ui-{ver}.custom/jquery-ui.theme.css'.format(ver=jq_ui_ver),
        'js/fullcalendar-{ver}/fullcalendar.css'.format(ver=fullcalendar_ver),
        # next line causes rendering problems. See https://stackoverflow.com/questions/25681573/fullcalendar-header-buttons-missing
        # 'fullcalendar/{ver}/fullcalendar.print.css'.format(fullcalendar_ver),

        'style.css',
        'frontend/style.css',
        'eventscalendar.css',

        filters=['cssrewrite', 'cssmin'],
        output='gen/frontend.css',
        ),

    'materialize-js': materialize_bundle_js,

    'materialize-css': materialize_bundle_css,

    'page-events-servicesquery-js' : Bundle(
        materialize_bundle_js,
        'frontend/events-servicesquery.js',
        filters='jsmin',
        output='gen/events-servicesquery.js',
        ),

    'admin_js': Bundle(
        'js/jQuery-{ver}/jquery-{ver}.js'.format(ver=jq_ver),
        'js/jquery-ui-{ver}.custom/jquery-ui.js'.format(ver=jq_ui_ver),

        'js/lodash-{ver}/lodash.js'.format(ver=lodash_ver),

        'js/DataTables-{ver}/js/jquery.dataTables.js'.format(ver=dt_datatables_ver),
        'js/DataTables-{ver}/js/dataTables.jqueryui.js'.format(ver=dt_datatables_ver),

        'js/Buttons-{ver}/js/dataTables.buttons.js'.format(ver=dt_buttons_ver),
        'js/Buttons-{ver}/js/buttons.jqueryui.js'.format(ver=dt_buttons_ver),
        'js/Buttons-{ver}/js/buttons.html5.js'.format(ver=dt_buttons_ver),
        'js/Buttons-{ver}/js/buttons.colVis.js'.format(ver=dt_colvis_ver), 

        'js/FixedColumns-{ver}/js/dataTables.fixedColumns.js'.format(ver=dt_fixedcolumns_ver),

        'js/Editor-{ver}/js/dataTables.editor.js'.format(ver=dt_editor_ver),
        'js/Editor-{ver}/js/editor.jqueryui.js'.format(ver=dt_editor_ver),

        'js/Select-{ver}/js/dataTables.select.js'.format(ver=dt_select_ver),

        # select2 is required for use by Editor forms
        'js/select2-{ver}/js/select2.full.js'.format(ver=s2_ver),
        # the order here is important
        'js/FieldType-Select2/editor.select2.js',

        # date time formatting for datatables editor, per https://editor.datatables.net/reference/field/datetime
        'js/moment-{ver}/moment.js'.format(ver=moment_ver),

        'js/yadcf-{ver}/jquery.dataTables.yadcf.js'.format(ver=yadcf_ver),

        'js/fullcalendar-{ver}/fullcalendar.js'.format(ver=fullcalendar_ver),

        'admin/editor.googledoc.js',
        'admin/layout.js',
        'admin/crudapi.js',
        'admin/datatables.js',
        'admin/events.js',
        'admin/editor.select2.mymethods.js',
        'legend.js',
        'admin/admin_eventscalendar.js',

        output='gen/admin.js',
        filters='jsmin',
        ),

    'admin_css': Bundle(
        'js/jquery-ui-{ver}.custom/jquery-ui.css'.format(ver=jq_ui_ver),
        'js/jquery-ui-{ver}.custom/jquery-ui.structure.css'.format(ver=jq_ui_ver),
        'js/jquery-ui-{ver}.custom/jquery-ui.theme.css'.format(ver=jq_ui_ver),
        'js/DataTables-{ver}/css/dataTables.jqueryui.css'.format(ver=dt_datatables_ver),
        'js/Buttons-{ver}/css/buttons.jqueryui.css'.format(ver=dt_buttons_ver),
        'js/FixedColumns-{ver}/css/fixedColumns.jqueryui.css'.format(ver=dt_fixedcolumns_ver),
        'js/Editor-{ver}/css/editor.jqueryui.css'.format(ver=dt_editor_ver),
        'js/Select-{ver}/css/select.jqueryui.css'.format(ver=dt_select_ver),
        'js/select2-{ver}/css/select2.css'.format(ver=s2_ver),
        'js/yadcf-{ver}/jquery.dataTables.yadcf.css'.format(ver=yadcf_ver),
        'js/fullcalendar-{ver}/fullcalendar.css'.format(ver=fullcalendar_ver),

        'style.css',
        'admin/style.css',
        'admin/editor-forms.css', 
        'admin/events.css',
        'eventscalendar.css',

        output='gen/admin.css',
        # cssrewrite helps find image files when ASSETS_DEBUG = False
        filters=['cssrewrite', 'cssmin'],
        )
}

asset_env = Environment()
