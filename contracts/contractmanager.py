###########################################################################################
# contracts - contracts views
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/13/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
contract - class and helpers to manage contract
==================================================
'''

# standard
from tempfile import mkdtemp
from datetime import date
from os.path import join as pathjoin
from copy import deepcopy
from csv import reader
from shutil import rmtree
from json import loads

# pypy
from docx import Document
from flask import current_app
from jinja2 import Environment
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# homegrown
from contracts.dbmodel import db, Contract, ContractType
from loutilities import timeu
from loutilities.googleauth import get_credentials
from contracts.views.admin.login import APP_CRED_FOLDER

class parameterError(Exception): pass

debug = True
debug2 = False

# templating environment. strip white space. see http://jinja.pocoo.org/docs/2.10/templates/#whitespace-control
template_env = Environment(trim_blocks=True, lstrip_blocks=True)

# needful constants
DRIVE_SERVICE = 'drive'
DRIVE_VERSION = 'v3'

# exceptions
class PermissionError(Exception): pass

#----------------------------------------------------------------------
def _evaluate(tree, subtree):
#----------------------------------------------------------------------
    '''
    detect callable attributes of the subtree object, and evaluate them
    by replacing with result of subtree.attr(tree)
    '''
    # adapted from https://stackoverflow.com/questions/7963762/what-is-the-most-economical-way-to-convert-nested-python-objects-to-dictionaries
    # if at a leaf, either return the leaf of leaf(tree)
    if not hasattr(subtree, '__dict__'):
        if not callable(subtree):
            return subtree
        else:
            return subtree(tree)

    # flow here if we have an object
    for key, val in subtree.__dict__.items():
        if key.startswith('_'): continue

        element = []
        if isinstance(val, list):
            for item in val:
                if debug2: current_app.logger.debug('_evaluate(): processing list item key={} item={}'.format(key, item))
                element.append( _evaluate( tree, item ) )
        else:
            element = _evaluate( tree, getattr(subtree, key) )

        if debug2: current_app.logger.debug('_evaluate(): key={} element={}'.format(key, element))
        setattr( subtree, key, element )

    # bubble up the results
    return subtree

#####################################################
class ContractManagerTemplate():
#####################################################
    '''
    parameters:

    * template - jinja2 template of text with replacement fields surrounded by curly braces with fields 
      like {{ a }, {{ b.c }} and control like {% for xxx %} {% endfor %}, {% if xxx %} {% endif %} 
      see http://jinja.pocoo.org/docs/2.10/templates/
    '''

    #----------------------------------------------------------------------
    def __init__(self, template):
    #----------------------------------------------------------------------
        if debug: current_app.logger.debug('ContractManager.__init__(): template={}'.format(template))
        self.template = template_env.from_string(template)

    #----------------------------------------------------------------------
    def render(self, mergefields):
    #----------------------------------------------------------------------
        '''
        merge a template of document output based on mergefields

        parameters:

        * merge - object containing items to be substituted into format strings, may have callable items  
          top level is turned into dict and subsequent levels are treated as attributes
        '''
        # preprocess any callable leaves
        merge = _evaluate(mergefields, mergefields)

        # render the template
        if debug: current_app.logger.debug('ContractManager.render(): merge={}'.format(merge.__dict__))
        evaluated = self.template.render(**merge.__dict__)

        return evaluated
    
    #----------------------------------------------------------------------
    def generate(self, mergefields):
    #----------------------------------------------------------------------
        '''
        create jinja2 generator to render text incrementally.

        parameters:

        * takes same arguments as render

        returns: generator object, generator.next() yields next section or raises StopIteration
        '''
        # preprocess any callable leaves
        merge = _evaluate(mergefields, mergefields)

        # create the template generator
        if debug: current_app.logger.debug('ContractManager.generate(): merge={}'.format(merge.__dict__))
        generator = self.template.generate(**merge.__dict__)

        return generator

#####################################################
class ContractManager():
#####################################################
    '''
    manage contract creation, storage and retrieval

    parameters:

    * contracttype - type of contract
    * driveFolder - folder id on google drive to store contract document
    '''

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
    #----------------------------------------------------------------------
        # the args dict has default values for arguments added by this class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(contractType=None,
                    driveFolderId=None,
                    )
        args.update(kwargs)
        for key in args:
            setattr(self, key, args[key])

    #----------------------------------------------------------------------
    def create(self, filename, mergefields, addlfields={}):
    #----------------------------------------------------------------------
        '''
        create the document

        parameters:

        * filename - name of file to be created
        * mergefields - flat dict with keys to be used as merge fields. If field contains 
          a function, the function is called with a single argument: the original mergefields itself
        * any fields to be added to mergefields

        returns: G Suite document id
        '''

        # docx handle
        docx = Document()

        # retrieve contract template
        templates = db.session.query(Contract).filter(Contract.contractTypeId==ContractType.id).filter(ContractType.contractType==self.contractType).order_by(Contract.blockPriority).all()

        # prepare built in fields
        dt = timeu.asctime('%B %d, %Y')
        _date_ = dt.dt2asc( date.today() )
        
        # copy caller's mergefields and add built-in fields
        merge = deepcopy(mergefields)
        merge._date_ = _date_

        # maybe there are some additional fields
        for key in addlfields:
            setattr(merge, key, addlfields[key])

        # fill contents
        for blockd in templates:
            # retrieve block type text
            blockType = blockd.contractBlockType.blockType

            # para is a single paragraph, based on a single template
            if blockType == 'para':
                template = ContractManagerTemplate( blockd.block )
                para = docx.add_paragraph( template.render( merge ) )

            # sectionprops has json object containing section property assignments (see https://python-docx.readthedocs.io/en/latest/api/section.html)
            elif blockType == 'sectionprops':
                props = loads( blockd.block )
                for prop in props:
                    # try to convert property value, otherwise leave as string
                    thisprop = props[prop]
                    for ttype in [int, float]:
                        try:
                            thisprop = ttype(thisprop)
                            break
                        except ValueError:
                            pass
                    setattr(docx.sections[0], prop, thisprop)

            # listitem[2] is a list item which may generate multiple lines, based on a single template
            elif blockType in ['listitem', 'listitem2']:
                template = ContractManagerTemplate( blockd.block )
                for render in template.generate( merge ):
                    listitem = docx.add_paragraph( render )
                    if blockType == 'listitem':
                        listitem.style = 'List Bullet'
                    elif blockType == 'listitem2':
                        listitem.style = 'List Bullet 2'
                
            # pagebreak is, well, just a page break
            elif blockType == 'pagebreak':
                docx.add_page_break()
                
            # tablehdr causes a table to be created with the number of columns depending on how many elements
            # this is configured as comma separated headings (no template rendering is done)
            elif blockType == 'tablehdr':
                # use csv reader to parse quoted fields with commas correctly
                rdr = reader([blockd.block])
                headings = rdr.next()
                table = docx.add_table(rows=1, cols=len(headings))
                hdr_cells = table.rows[0].cells
                for c in range(len(headings)):
                    run = hdr_cells[c].paragraphs[0].add_run( headings[c] )
                    run.bold = True

            # tablerow and tablerowbold define what some rows of the table look like
            # this is configured as template with comma separated columns, optional for loop
            elif blockType in ['tablerow', 'tablerowbold']:
                # get templated and create generator
                coltemplate = ContractManagerTemplate( blockd.block )
                colg = coltemplate.generate( merge )

                # collect the generated raw rows (raw means with commas embedded)
                rawrows = []
                for rawrow in colg:
                    rawrows.append( rawrow )

                # then add row data to table using csv reader 
                # if there are commas in the data csv reader will parse quoted fields with commas correctly
                rows = reader( rawrows )
                for row in rows:
                    row_cells = table.add_row().cells
                    for c in range(len(row)):
                        run = row_cells[c].paragraphs[0].add_run( row[c] )
                        if blockType == 'tablerowbold':
                            run.bold = True
            
            else:
                raise parameterError, 'unknown block type: {}'.format(blockType)

        # save temporary doc file
        dirpath = mkdtemp(prefix='contracts_')
        path = pathjoin(dirpath, filename)
        docx.save(path)
        if debug: current_app.logger.debug('ContractManager.create(): created temporary {}'.format(path))

        # upload to google drive
        ## load credentials for drive instance
        credentials = get_credentials(APP_CRED_FOLDER)
        if not credentials:
            return redirect('authorize')

        ## set up drive service
        drive = build(DRIVE_SERVICE, DRIVE_VERSION, credentials=credentials)

        ## upload (adapted from https://developers.google.com/drive/api/v3/manage-uploads)
        drivename = filename
        if drivename[-5:] == '.docx': drivename = drivename[:-5]
        file_metadata = {
            'name': drivename,
            # see https://developers.google.com/drive/api/v3/mime-types
            'mimeType': 'application/vnd.google-apps.document',
            # see https://developers.google.com/drive/api/v3/folder
            'parents': [current_app.config['CONTRACTS_DB_FOLDER']],
        }
        media = MediaFileUpload(path,
            # see https://blogs.msdn.microsoft.com/vsofficedeveloper/2008/05/08/office-2007-file-format-mime-types-for-http-content-streaming-2/
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            resumable=True)
        file = drive.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
        fid = file.get('id')
        if debug: current_app.logger.debug('uploaded fid={}'.format(fid))

        ## TODO: set file to be publicly readable
        # see https://developers.google.com/drive/api/v3/manage-sharing
        def batch_callback(request_id, response, exception):
            if exception:
                # Handle error
                if debug: current_app.logger.error("batch_callback(): permission exception {}".format(exception) )
                raise PermissionError, exception
            else:
                if debug: current_app.logger.debug("batch_callback(): permission id {}".format(response.get('id')) )

        batch = drive.new_batch_http_request(callback=batch_callback)
        public_permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        batch.add(drive.permissions().create(
                fileId=fid,
                body=public_permission,
                fields='id',
        ))
        batch.execute()

        # remove temporary folder
        # NOTE: in windows at least, this gets an error because file is still in use
        rmtree(dirpath, ignore_errors=True)

        # send email

        return fid


