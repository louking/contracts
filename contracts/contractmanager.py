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

# homegrown
from contracts.dbmodel import db, Contract, ContractType
from loutilities import timeu

class parameterError(Exception): pass

debug = True

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
    @staticmethod
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
                    element.append( ContractManager._evaluate( tree, getattr(subtree, key) ) )
            else:
                element = ContractManager._evaluate( tree, getattr(subtree, key) )

            setattr( subtree, key, element )

        # bubble up the results
        return subtree

    #----------------------------------------------------------------------
    @staticmethod
    def _format(block, mergefields):
    #----------------------------------------------------------------------
        '''
        merge a block of document output based on mergefields

        parameters:

        * block - block of text with replacement fields surrounded by curly braces with fields like {a}, {b.c}
        * merge - object containing items to be substituted into format strings, may have callable items  
          top level is turned into dict and subsequent levels are treated as attributes
        '''
        merge = ContractManager._evaluate(mergefields, mergefields)

        # evaluate the block
        if debug: current_app.logger.debug('ContractManager._format(): block={} merge={}'.format(block,merge))
        evaluated = block.format(**merge.__dict__)

        return evaluated
    
    #----------------------------------------------------------------------
    def create(self, filename, mergefields):
    #----------------------------------------------------------------------
        '''
        create the document

        parameters:

        * filename - name of file to be created
        * mergefields - flat dict with keys to be used as merge fields. If field contains 
          a function, the function is called with a single argument: the original mergefields itself

        returns: G Suite document id
        '''

        # docx handle
        docx = Document()

        # retrieve contract template
        template = db.session.query(Contract).filter(Contract.contractTypeId==ContractType.id).filter(ContractType.contractType==self.contractType).order_by(Contract.blockPriority).all()

        # prepare built in fields
        dt = timeu.asctime('%B %d, %Y')
        _date_ = dt.dt2asc( date.today() )
        
        # copy caller's mergefields and add built-in fields
        merge = deepcopy(mergefields)
        merge._date_ = _date_
        # merge.update( {
        #         '_date_' : _date_,
        #     } )
        
        # fill contents
        for blockd in template:
            # retrieve block type text
            blockType = blockd.contractBlockType.blockType
            block = blockd.block

            if blockType == 'para':
                para = docx.add_paragraph(ContractManager._format(block, merge))

            elif blockType == 'listitem':
                pass
                
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


