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

# pypy
from docx import Document
from flask import current_app
from jinja2 import Environment

# homegrown
from contracts.dbmodel import db, Contract, ContractType
from loutilities import timeu

class parameterError(Exception): pass

debug = True
debug2 = False

# templating environment. strip white space. see http://jinja.pocoo.org/docs/2.10/templates/#whitespace-control
template_env = Environment(trim_blocks=True, lstrip_blocks=True)

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

    #----------------------------------------------------------------------
    def __init__(self, template):
    #----------------------------------------------------------------------
        '''
        * template - jinja2 template of text with replacement fields surrounded by curly braces with fields 
          like {{ a }, {{ b.c }} and control like {% for xxx %} {% endfor %}, {% if xxx %} {% endif %} 
          see http://jinja.pocoo.org/docs/2.10/templates/
        '''
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
            template = ContractManagerTemplate( blockd.block )

            if blockType == 'para':
                para = docx.add_paragraph( template.render( merge ) )

            elif blockType in ['listitem', 'listitem2']:
                for render in template.generate( merge ):
                    listitem = docx.add_paragraph( render )
                    if blockType == 'listitem':
                        listitem.style = 'List Bullet'
                    elif blockType == 'listitem2':
                        listitem.style = 'List Bullet 2'
                
            elif blockType == 'tablehdr':
                pass
                
            elif blockType == 'tablerow':
                pass
            
            else:
                raise parameterError, 'unknown block type: {}'.format(blockType)

        # save temporary doc file
        dirpath = mkdtemp()
        path = pathjoin(dirpath, filename)
        docx.save(path)
        if debug: current_app.logger.debug('ContractManager.create(): created temporary {}'.format(path))

        # upload to google drive

        # remove temporary folder


