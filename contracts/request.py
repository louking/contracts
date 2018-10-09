###########################################################################################
# request - generic request processing
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/06/18        Lou King        Create (from https://raw.githubusercontent.com/louking/rrwebapp/master/rrwebapp/request.py)
#
#   Copyright 2018 Lou King.  All rights reserved
#
###########################################################################################

# standard
import os
import os.path
import stat
from datetime import timedelta
from functools import update_wrapper

# pypi
from flask import url_for, make_response, request, current_app
from flask_login import login_required
from flask.views import MethodView

# module specific needs
# from nav import setnavigation

class invalidScript(Exception): pass

# all scripts required by this application are specified here
# scripts are listed in the order they must be processed
# all css scripts are processed before all js scripts - see layout.jinja2 for details

# in SCRIPTS files from a CDN are contained in (filename, version, cdn) tuples
#    cdn is host for content data network
#    filename may contain {ver}, {min} as replacement_field {field_name}
#    {min} gets replaced with '.min' if current_app.config['MINIMIZE_CDN_JAVASCRIPT'] is True
#    {ver} gets replaced with version

# if scriptitem in request.SCRIPTS is not a tuple, it is assumed to be the string filename 
# of a file located in server static directory. v arg is set to modification time of the
# file to assure updated files will be downloaded (i.e., cache won't be used)

# jquery
jq_cdn = 'https://code.jquery.com'
jq_ver = '3.3.1'
jq_ui_cdn = 'https://code.jquery.com/ui'
jq_ui_ver = '1.12.1'


# dataTables
dt_cdn = 'https://cdn.datatables.net'
dt_datatables_ver = '1.10.18'
dt_buttons_ver = '1.5.2'
dt_colvis_ver = '1.5.2'
dt_fixedcolumns_ver = '3.2.5'
dt_select_ver = '1.2.6'
dt_editor_plugin_cdn = 'https://editor.datatables.net/plug-ins/download?cdn=cdn-download&amp;q='
dt_editor_plugin_fieldtype_ver = '?'

# select2
# NOTE: patch to jquery ui required, see https://github.com/select2/select2/issues/1246#issuecomment-17428249
# currently in datatables.js
s2_cdn = 'https://cdnjs.cloudflare.com/ajax/libs'
s2_ver = '4.0.3'

# selectize
sz_cdn = 'https://cdnjs.cloudflare.com/ajax/libs'
sz_ver = '0.12.4'

# yadcf
yadcf_cdn = 'https://cdnjs.cloudflare.com/ajax/libs'
yadcf_ver = '0.9.1'

# d3
d3_cdn = 'https://d3js.org'
d3_ver = 'v4'
d3_sc_ver = 'v1'    # d3-scale-chromatic

# moment.js (see https://momentjs.com/)
moment_cdn = 'https://cdnjs.cloudflare.com/ajax/libs'
moment_ver = '2.22.2'

SCRIPTS = [
    ('jquery-{ver}{min}.js', jq_ver, jq_cdn),

    # ('{ver}/jquery-ui{min}.js', jq_ui_ver, jq_ui_cdn),
    # ('{ver}/themes/smoothness/jquery-ui{min}.css', jq_ui_ver, jq_ui_cdn),
    'js/jquery-ui-1.12.1.custom/jquery-ui{min}.js',
    'js/jquery-ui-1.12.1.custom/jquery-ui{min}.css', 
    'js/jquery-ui-1.12.1.custom/jquery-ui.structure{min}.css', 
    'js/jquery-ui-1.12.1.custom/jquery-ui.theme{min}.css', 

    ('{ver}/js/jquery.dataTables{min}.js', dt_datatables_ver, dt_cdn),
    ('{ver}/js/dataTables.jqueryui{min}.js', dt_datatables_ver, dt_cdn),
    ('{ver}/css/dataTables.jqueryui{min}.css', dt_datatables_ver, dt_cdn),

    ('buttons/{ver}/js/dataTables.buttons{min}.js', dt_buttons_ver, dt_cdn),
    ('buttons/{ver}/js/buttons.jqueryui.js', dt_buttons_ver, dt_cdn),

    ('buttons/{ver}/js/buttons.html5{min}.js', dt_buttons_ver, dt_cdn),
    ('buttons/{ver}/css/buttons.jqueryui{min}.css', dt_buttons_ver, dt_cdn),

    ('buttons/{ver}/js/buttons.colVis{min}.js', dt_colvis_ver, dt_cdn), 

    ('fixedcolumns/{ver}/js/dataTables.fixedColumns{min}.js', dt_fixedcolumns_ver, dt_cdn),
    ('fixedcolumns/{ver}/css/fixedColumns.jqueryui{min}.css', dt_fixedcolumns_ver, dt_cdn),

    # Editor is not yet available from the dataTables CDN
    'js/Editor-1.8.0/js/dataTables.editor.js',
    'js/Editor-1.8.0/js/editor.jqueryui.js',
    'js/Editor-1.8.0/css/editor.jqueryui.css',

    ('select/{ver}/js/dataTables.select.js', dt_select_ver, dt_cdn),
    ('select/{ver}/css/select.jqueryui.css', dt_select_ver, dt_cdn),

    # select2 is required for use by Editor forms
    ('select2/{ver}/js/select2.full{min}.js', s2_ver, s2_cdn),
    ('select2/{ver}/css/select2{min}.css', s2_ver, s2_cdn),
    'js/FieldType-Select2/editor.select2.js',

    # date time formatting for datatables editor, per https://editor.datatables.net/reference/field/datetime
    ('moment.js/{ver}/moment{min}.js', moment_ver, moment_cdn),

    ('yadcf/{ver}/jquery.dataTables.yadcf{min}.js', yadcf_ver, yadcf_cdn),
    ('yadcf/{ver}/jquery.dataTables.yadcf{min}.css', yadcf_ver, yadcf_cdn),

    # 'js/jquery.ui.dialog-clickoutside.js', # from https://github.com/coheractio/jQuery-UI-Dialog-ClickOutside

    'layout.js',
    'style.css',
]

#----------------------------------------------------------------------
def annotatescripts(scripts):
#----------------------------------------------------------------------
    '''
    annotate scripts with version = file timestamp
    this is used to force browser to reload script file when it changes

    in scripts files from a CDN are contained in (filename, version, cdn) tuples
       cdn is host for content data network
       filename may contain {ver}, {min} as replacement_field {field_name}
       {min} gets replaced with '.min' if current_app.config['MINIMIZE_CDN_JAVASCRIPT'] is True
       {ver} gets replaced with version

    if scriptitem in request.SCRIPTS is not a tuple, it is assumed to be the string filename 
    of a file located in server static directory. v arg is set to modification time of the
    file to assure updated files will be downloaded (i.e., cache won't be used)

    :param scripts: list of scriptitems to annotate
    :rtype: list of {'filename':filename, 'version':version}

    '''
    annotated = []
    
    for scriptitem in scripts:
        # handle CDN items
        # maybe get minimized version
        cdnmin = ''
        if 'MINIMIZE_CDN_JAVASCRIPT' in current_app.config and current_app.config['MINIMIZE_CDN_JAVASCRIPT']:
            cdnmin = '.min'
        if type(scriptitem) == tuple:
            thisfile, version, cdn = scriptitem


            # format based on whether query options are already included
            # cdn non-trivial and query options not present
            if cdn and '?' not in cdn:
                # remove any trailing '/' from cdn
                if cdn[-1] == '/':
                    cdn = cdn[:-1]
                fileref = '{}/{}?v={}'.format(cdn,thisfile.format(ver=version,min=cdnmin),version)
            # query options already present
            # NOTE: this part of the logic doesn't work because somewhere string is getting url quoted
            else:
                fileref = '{}{}&v={}'.format(cdn,thisfile.format(ver=version,min=cdnmin),version)
        
        # handle static file items
        else:
            thisfile = scriptitem.format(min=cdnmin)
            filepath = os.path.join(current_app.static_folder,thisfile)
            version = os.stat(filepath)[stat.ST_MTIME]
            fileurl = url_for('static', filename=thisfile)
            fileref = '{}?v={}'.format(fileurl, version)
        
        annotated.append(fileref)

    return annotated
    
#----------------------------------------------------------------------
def setscripts():
#----------------------------------------------------------------------
    '''
    setscripts caches the versions for js and css scripts, identified in
    request.SCRIPTS

    files from a CDN are contained in (filename, version, cdn) tuples
       cdn is host for content data network
       filename may contain {ver}, {min} as replacement_field {field_name}
       {min} gets replaced with '.min' if current_app.config['MINIMIZE_CDN_JAVASCRIPT'] is True
       {ver} gets replaced with version

    if item in request.SCRIPTS is not a tuple, it is assumed to be the string filename 
    of a file located in server static directory
    '''
    cssfiles = []
    jsfiles = []
    for scriptitem in SCRIPTS:
        # handle files from CDN
        if type(scriptitem) == tuple:
            thisfile = scriptitem[0]
        
        # handle static files
        else:
            thisfile = scriptitem

        filetype = thisfile.split('.')[-1]  # gets file extension

        # append scriptitem to list, might be cdn tuple
        # annotatescripts() parses and puts correct filename / version string
        if filetype == 'css':
            cssfiles.append(scriptitem)
        elif filetype == 'js':
            jsfiles.append(scriptitem)
        else:
            raise invalidScript,'Invalid script filename: {}'.format(thisfile)
    
    # make these available to any template
    current_app.jinja_env.globals['_cssfiles'] = annotatescripts(cssfiles)
    current_app.jinja_env.globals['_jsfiles'] = annotatescripts(jsfiles)
    
#----------------------------------------------------------------------
def addscripts(scriptlist):
#----------------------------------------------------------------------
    '''
    return script tags for designated filenames. the result must be passed into
    template to be added to standard scripts. this can be used for js or css files
    but all in the list must be the same

    :param scriptlist: list of local filenames to be added to the jsfiles list when template is built
    :rtype: list of annotated scripts to be passed to template
    '''
    
    if len(scriptlist) == 0:
        return []

    # get filetype of first file
    firstfiletype = scriptlist[0].split('.')[-1]
    if firstfiletype not in ['css', 'js']:
        raise invalidScript,'Invalid script filename: {}'.format(thisfile)

    # make sure all scripts referenced are of same type as first
    for thisfile in scriptlist:
        filetype = thisfile.split('.')[-1]
        if filetype != firstfiletype:
            raise invalidScript,'All scripts in script list must be of same type: {}'.format(scriptlist)

    return annotatescripts(scriptlist)

# #----------------------------------------------------------------------
# @current_app.before_request
# def before_request():
# #----------------------------------------------------------------------
#     setnavigation()

#----------------------------------------------------------------------
@current_app.after_request
def after_request(response):
#----------------------------------------------------------------------
    if not current_app.config['DEBUG']:
        current_app.logger.info('{}: {} {} {}'.format(request.remote_addr, request.method, request.url, response.status_code))
    return response


#----------------------------------------------------------------------
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
#----------------------------------------------------------------------
    '''
    crossdomain decorator

    methods: Optionally a list of methods that are allowed for this view. If not provided it will allow all methods that are implemented.
    headers: Optionally a list of headers that are allowed for this request.
    origin: '*' to allow all origins, otherwise a string with a URL or a list of URLs that might access the resource.
    max_age: The number of seconds as integer or timedelta object for which the preflighted request is valid.
    attach_to_all: True if the decorator should add the access control headers to all HTTP methods or False if it should only add them to OPTIONS responses.
    automatic_options: If enabled the decorator will use the default Flask OPTIONS response and attach the headers there, otherwise the view function will be called to generate an appropriate response.

    from http://flask.pocoo.org/snippets/56/
    '''
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator