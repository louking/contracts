###########################################################################################
# eventscontract - handle contract management for race services contract
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/15/18        Lou King        Create
#
#   Copyright 2018 Lou King
###########################################################################################
'''
eventscontract - handle contract management for race services contract
===========================================================================
'''
# standard
from datetime import date
from copy import deepcopy

# pypi
from flask import current_app, url_for, request
from jinja2 import Template
from loutilities.flask_helpers.mailer import sendmail
from loutilities.tables import DbCrudApiRolePermissions, get_request_data
from loutilities.timeu import asctime

# homegrown
from ...dbmodel import db, Event, State, FeeBasedOn, Contract, ContractType, TemplateType
from ...dbmodel import STATE_COMMITTED, STATE_CONTRACT_SENT
from ...contractmanager import ContractManager

dt = asctime('%Y-%m-%d')

class parameterError(Exception): pass

debug = True

###########################################################################################
class EventsContract(DbCrudApiRolePermissions):
###########################################################################################
    '''
    extend DbCrudApiRolePermissions to handle send contract request within put() [edit] method
    '''
    #----------------------------------------------------------------------
    def editor_method_posthook(self, form):
    #----------------------------------------------------------------------
        '''
        send contract to client contact if asked to do so, after processing put()

        note row has already been committed to the database, so can be retrieved
        '''
        # the following can be true only for put() [edit] method
        if 'addlaction' in form and form['addlaction'] in ['sendcontract', 'resendcontract', 'initiateinvoice']:
            folderid = current_app.config['CONTRACTS_DB_FOLDER']
            
            # quote or invoice?
            if form['addlaction'] == 'initiateinvoice':
                doctype = 'INVOICE'
                templatetype = 'invoice email'
                is_quote = False
            else:
                doctype = 'AGREEMENT/QUOTE'
                templatetype = 'agreement accepted view'
                is_quote = True

            # need an instance of contract manager to take care of saving the contract
            cm = ContractManager(contractType='race services', templateType='contract', driveFolderId=folderid)

            # pull record(s) from database and save as flat dotted record
            data = get_request_data(form)
            print(('data={}'.format(data)))
            
            # there's only going to be one id -- this sort of supports multi-edit, but that won't happen
            for thisid in data:
                eventdb = Event.query.filter_by(id=thisid).one()

                # different subject line if contract had been accepted before. This must match contractviews.AcceptAgreement.post
                annotation = ''

                # if we are generating a new version of the contract/invoice
                if form['addlaction'] in ['sendcontract', 'initiateinvoice']:
                    # maybe it's an update to the contract or invoice
                    # if there was already a document sent, indicate that we're updating it
                    if is_quote and eventdb.contractDocId:
                        # isContractUpdated is used to annotate the contract accepted email in contractviews.AcceptAgreement.post()
                        eventdb.isContractUpdated = True
                        annotation = '(updated) '
                    elif not is_quote and eventdb.invoiceDocId:
                        annotation = '(updated) '

                    # check appropriate fields are present for certain services
                    servicenames = {s.service for s in eventdb.services}
                    if servicenames & {'coursemarking', 'finishline'}:
                        self._fielderrors = []
                        for field in ['race', 'date', 'mainStartTime', 'mainDistance' ]:
                            if not data[thisid][field]:
                                self._fielderrors.append({ 'name' : field, 'status' : 'please supply'})
                        ## handle select fields
                        for field in ['state', 'services', 'client', 'course', 'lead']:
                            if not data[thisid][field]['id']:
                                self._fielderrors.append({ 'name' : '{}.id'.format(field), 'status' : 'please select'})
                        if self._fielderrors:
                            raise parameterError('missing fields')


                    # calculate service fees
                    servicefees = []

                    feetotal = 0
                    for service in eventdb.services:
                        servicefee = { 'service' : service.serviceLong }
                        # fixed fee
                        if service.feeType.feeType =='fixed':
                            thisfee = service.fee
                            servicefee.update( {'fee':thisfee, 'qty': '', 'unitfee': 'fixed' } ) 
                            servicefees.append( servicefee )

                        # fee is based on another field
                        elif service.feeType.feeType =='basedOnField':
                            field = service.basedOnField
                            # not clear why this needs to be converted to int, but otherwise see unicode value
                            # if can't be converted, then invalid format
                            try:
                                fieldval = int(getattr(eventdb, field))
                            except (TypeError, ValueError) as e:
                                fieldval = None

                            # field not set, then set self._fielderrors appropriately
                            if not fieldval:
                                formfield = self.dbmapping[field]   # hopefully not a function
                                self._fielderrors = [{ 'name' : formfield, 'status' : 'needed to calculate fee' }]
                                raise parameterError('cannot calculate fee if {} not set'.format(field))

                            feebasedons = FeeBasedOn.query.filter_by(serviceId=service.id).order_by(FeeBasedOn.fieldValue).all()
                            foundfee = False
                            for feebasedon in feebasedons:
                                lastfieldval = feebasedon.fieldValue
                                if debug: current_app.logger.debug('fieldval={} feebasedon.fieldValue={}'.format(fieldval, feebasedon.fieldValue))
                                if debug: current_app.logger.debug('type(fieldval)={} type(feebasedon.fieldValue)={}'.format(type(fieldval), type(feebasedon.fieldValue)))
                                if fieldval <= feebasedon.fieldValue:
                                    thisfee = feebasedon.fee
                                    servicefee.update( {'fee':thisfee, 'qty':fieldval, 'unitfee': 'fixed' } ) 
                                    servicefees.append( servicefee )
                                    foundfee = True
                                    break

                            # if fee not found, then set fielderrors appropriately
                            if not foundfee:
                                formfield = self.dbmapping[field]   # hopefully not a function
                                self._fielderrors = [{ 'name' : formfield, 'status' : 'cannot calculate fee if this is greater than {}'.format(lastfieldval) }]
                                raise parameterError('cannot calculate fee if {} greater than {}'.format(field, lastfieldval))
                                
                        # not sure how we could get here, but best to be defensive
                        else:
                            raise parameterError('unknown feeType: {}'.format(service.feeType.feeType))

                        # accumulate total fee
                        feetotal += thisfee

                    # need to calculate addons in addition to services (note automatically sorted by priority)
                    for addon in eventdb.addOns:
                        servicefee = {'service': addon.longDescr}
                        if not addon.is_upricing:
                            thisfee = addon.fee
                            servicefee.update({'fee': thisfee, 'qty': '', 'unitfee': 'fixed'})
                        else:
                            qty = getattr(eventdb, addon.up_basedon) - addon.up_subfixed
                            if qty < 0:
                                qty = 0
                            thisfee = addon.fee * qty
                            servicefee.update({'fee': thisfee, 'qty':qty, 'unitfee': f'${addon.fee}'})
                        servicefees.append(servicefee)

                        # accumulate total fee
                        feetotal += thisfee

                    # generate contract / invoice
                    if debug: current_app.logger.debug('editor_method_posthook(): (before create()) eventdb.__dict__={}'.format(eventdb.__dict__))
                    docid = cm.create('{}-{}-{}.docx'.format(eventdb.client.client, eventdb.race.race, eventdb.date), eventdb, 
                                      addlfields={'servicenames': [s.service for s in eventdb.services],
                                                  'addons'      : [a.shortDescr for a in eventdb.addOns],
                                                  'doctype'     : doctype,
                                                  'is_quote'    : is_quote,
                                                  'servicefees' : servicefees,
                                                  'event'       : eventdb.race.race,
                                                  'totalfees'   : { 'service' : 'TOTAL', 'fee' : feetotal },
                                                 },
                                      is_quote=is_quote)
                    
                    # update database to show contract sent
                    if is_quote:
                        eventdb.state = State.query.filter_by(state=STATE_CONTRACT_SENT).one()
                        eventdb.contractDocId = docid
                        eventdb.contractSentDate = dt.dt2asc( date.today() )
                    else:
                        eventdb.invoiceDocId = docid
                    
                    # find index with correct id and show database updates
                    for resprow in self._responsedata:
                        if resprow['rowid'] == thisid: 
                            resprow['state'] = { key:val for (key,val) in list(eventdb.state.__dict__.items()) if key[0] != '_' }
                            resprow['contractSentDate'] = eventdb.contractSentDate
                            resprow['contractDocId'] = eventdb.contractDocId

                # if we are just resending current version of the contract
                else:
                    docid = eventdb.contractDocId
                    annotation = '(resend) '

                # email sent depends on current state as this flows from 'sendcontract' and 'resendcontract'
                if eventdb.state.state == STATE_COMMITTED:
                    # prepare agreement accepted or invoice email 
                    templatestr = (db.session.query(Contract)
                                   .filter(Contract.contractTypeId==ContractType.id)
                                   .filter(ContractType.contractType=='race services')
                                   .filter(Contract.templateTypeId==TemplateType.id)
                                   .filter(TemplateType.templateType==templatetype)
                                   .one()
                                  ).block
                    template = Template( templatestr )
                    if is_quote:
                        subject = f'{annotation}ACCEPTED - FSRC Race Services {doctype}: {eventdb.race.race} - {eventdb.date}'
                    else:
                        subject = f'{annotation}FSRC Race Services {doctype}: {eventdb.race.race} - {eventdb.date}'

                elif eventdb.state.state == STATE_CONTRACT_SENT:
                    # send contract mail to client
                    templatestr = (db.session.query(Contract)
                               .filter(Contract.contractTypeId==ContractType.id)
                               .filter(ContractType.contractType=='race services')
                               .filter(Contract.templateTypeId==TemplateType.id)
                               .filter(TemplateType.templateType=='contract email')
                               .one()
                              ).block
                    template = Template( templatestr )
                    subject = f'{annotation}FSRC Race Services {doctype}: {eventdb.race.race} - {eventdb.date}'

                # state must be STATE_COMMITTED or STATE_CONTRACT_SENT, else logic error
                else:
                    raise parameterError('editor_method_posthook(): bad state seen for {}: {}'.format(form['addlaction'], eventdb.state.state))

                # merge database fields into template and send email
                garbage = eventdb.client    # force load of subrecord
                mergefields = deepcopy(eventdb.__dict__)
                mergefields['viewcontracturl'] = 'https://docs.google.com/document/d/{}/view'.format(docid)
                mergefields['downloadcontracturl'] = 'https://docs.google.com/document/d/{}/export?format=pdf'.format(docid)
                # need to bring in full path for email, so use url_root
                mergefields['acceptcontracturl'] = request.url_root[:-1] + url_for('frontend.acceptagreement', docid=docid)
                mergefields['servicenames'] = [s.service for s in eventdb.services] 
                mergefields['addons'] = [a.shortDescr for a in eventdb.addOns] 
                mergefields['event'] = eventdb.race.race

                html = template.render( mergefields )
                # quote/agreement
                if is_quote:
                    tolist = eventdb.client.contactEmail
                    cclist = current_app.config['CONTRACTS_CC']
                # invoice
                else:
                    tolist = current_app.config['CONTRACTS_INVOICE_TO']
                    cclist = current_app.config['CONTRACTS_INVOICE_CC']
                fromlist = current_app.config['CONTRACTS_CONTACT']
                sendmail( subject, fromlist, tolist, html, ccaddr=cclist )
