###########################################################################################
# contractviews - views for contracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       06/29/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
contractviews - views for contracts database
=======================================================================
'''

# standard
import os.path
from copy import deepcopy

# pypi
from flask import current_app, render_template_string
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from jinja2 import Environment, FileSystemLoader

# home grown
from . import bp
from loutilities.flask_helpers.blueprints import add_url_rules
from contracts.dbmodel import db, Event, Contract, ContractType, TemplateType

debug = True

#######################################################################
class AcceptAgreement(MethodView):
#######################################################################
    url_rules = {
                'acceptagreement': ['/acceptagreement/<docid>',('GET','POST')],
                }

    #----------------------------------------------------------------------
    def get(self, docid):
    #----------------------------------------------------------------------
        from contracts.request import addscripts
        try:
            thisevent = Event.query.filter_by(contractDocId=docid).one()

        # Could not find docid in the database, so url used was obsolete
        # Tell user to request new email containing URL from contact
        except NoResultFound:
            templatestr = (db.session.query(Contract)
                           .filter(Contract.contractTypeId==ContractType.id)
                           .filter(ContractType.contractType=='race services')
                           .filter(Contract.templateTypeId==TemplateType.id)
                           .filter(TemplateType.templateType=='accept agreement error view')
                           .one()
                          ).block
            context = {
                       'pagename'          : 'contract not found',
                       'contracts_contact' : current_app.config['CONTRACTS_CONTACT'],
                       'pagecssfiles'      : addscripts(['frontend_style.css']),
                      }
            return render_template_string( templatestr, **context )


        # give user form to accept contract
        templatestr = (db.session.query(Contract)
                       .filter(Contract.contractTypeId==ContractType.id)
                       .filter(ContractType.contractType=='race services')
                       .filter(Contract.templateTypeId==TemplateType.id)
                       .filter(TemplateType.templateType=='accept agreement view')
                       .one()
                      ).block

        if debug: current_app.logger.debug('AcceptAgreement.get(): thisevent.__dict__={}'.format(thisevent.__dict__))
        thisevent.contracts_contact = current_app.config['CONTRACTS_CONTACT']
        thisevent.pagename = 'Accept Agreement'
        thisevent.pagecssfiles = addscripts(['frontend_style.css'])

        # need to reference client field so that this will be in __dict__
        clientgarbage = thisevent.client

        return render_template_string( templatestr, **thisevent.__dict__ )

#----------------------------------------------------------------------
add_url_rules(bp, AcceptAgreement)
#----------------------------------------------------------------------
