###########################################################################################
# contractviews - views for contracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       09/28/18        Lou King        Create
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
from json import loads
from datetime import date

# pypi
from flask import current_app, render_template_string, request, url_for
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from jinja2 import Template

# home grown
from . import bp
from contracts.dbmodel import db, Event, State, Contract, ContractType, TemplateType
from contracts.dbmodel import STATE_COMMITTED
from loutilities.flask_helpers.mailer import sendmail
from loutilities.flask_helpers.blueprints import add_url_rules
from loutilities.timeu import asctime

dt = asctime('%Y-%m-%d')

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
        # thisevent.pagename = 'Race Services Agreement'

        # drive urls
        # see https://www.labnol.org/internet/direct-links-for-google-drive/28356/
        webviewurl = 'https://docs.google.com/document/d/{}/view'.format(docid)
        thisevent.viewcontracturl = webviewurl
        pdfurl = 'https://docs.google.com/document/d/{}/export?format=pdf'.format(docid)
        thisevent.downloadcontracturl = pdfurl
        thisevent.agreeurl = url_for( '.acceptagreement', docid=docid )

        # force load of 'client' field so that it will be in __dict__
        clientgarbage = thisevent.client

        # make copy of the event for merging with the template
        mergefields = deepcopy(thisevent.__dict__)

        # page heading
        mergefields['pagename'] = 'accept agreement'

        # materialize bits
        mergefields['pageassets_css']   = 'materialize-css'
        mergefields['pageassets_js']    = 'materialize-js'

        return render_template_string( templatestr, **mergefields )

    #----------------------------------------------------------------------
    def post(self, docid):
    #----------------------------------------------------------------------
        # this should work because we just did get using same docid
        thisevent = Event.query.filter_by(contractDocId=docid).one()

        # get form fields and add to database
        name = request.form['name']
        email = request.form['email']
        notes = request.form['notes']
        thisevent.contractSignedDate = dt.dt2asc( date.today() )
        thisevent.contractApprover = name
        thisevent.contractApproverEmail = email
        thisevent.contractApproverNotes = notes
        thisevent.state = State.query.filter_by(state=STATE_COMMITTED).one()
        # need to get merge fields before commit, first force load of client
        clientgarbage = thisevent.client
        mergefields = deepcopy(thisevent.__dict__)
        db.session.commit()

        # prepare agreement accepted email and view
        templatestr = (db.session.query(Contract)
                       .filter(Contract.contractTypeId==ContractType.id)
                       .filter(ContractType.contractType=='race services')
                       .filter(Contract.templateTypeId==TemplateType.id)
                       .filter(TemplateType.templateType=='agreement accepted view')
                       .one()
                      ).block

        # add needed fields
        mergefields['servicenames'] = [s.service for s in thisevent.services] 
        mergefields['event'] = thisevent.race.race


        # drive urls
        # see https://www.labnol.org/internet/direct-links-for-google-drive/28356/
        webviewurl = 'https://docs.google.com/document/d/{}/view'.format(docid)
        mergefields['viewcontracturl'] = webviewurl
        pdfurl = 'https://docs.google.com/document/d/{}/export?format=pdf'.format(docid)
        mergefields['downloadcontracturl'] = pdfurl

        # send agreement accepted email
        template = Template( templatestr )
        html = template.render( mergefields )
        tolist = mergefields['client'].contactEmail
        cclist = current_app.config['CONTRACTS_CC']
        fromlist = current_app.config['CONTRACTS_CONTACT']
        print(('mergefields={}'.format(mergefields)))

        subject = 'ACCEPTED - FSRC Race Support Agreement: {} - {}'.format(mergefields['event'], mergefields['date'])
        sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

        # update for web view
        mergefields['webview'] = True

        if debug: current_app.logger.debug('AcceptAgreement.post(): mergefields={}'.format(mergefields))
        return render_template_string( templatestr, **mergefields )

#----------------------------------------------------------------------
add_url_rules(bp, AcceptAgreement)
#----------------------------------------------------------------------
