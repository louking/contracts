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

# homegrown
from contracts.dbmodel import db, Event, State, FeeBasedOn, Contract, ContractType, TemplateType
from contracts.dbmodel import STATE_COMMITTED, STATE_CONTRACT_SENT
from contracts.crudapi import DbCrudApiRolePermissions
from contracts.contractmanager import ContractManager
from contracts.mailer import sendmail
from loutilities.tables import get_request_data
from loutilities.timeu import asctime

dt = asctime('%Y-%m-%d')

class parameterError(Exception): pass

debug = True

###########################################################################################
class EventsApi(DbCrudApiRolePermissions):
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
        if 'addlaction' in form and form['addlaction'] in ['sendcontract', 'resendcontract']:
            folderid = current_app.config['CONTRACTS_DB_FOLDER']

            # need an instance of contract manager to take care of saving the contract
            cm = ContractManager(contractType='race services', templateType='contract', driveFolderId=folderid)

            # pull record(s) from database and save as flat dotted record
            data = get_request_data(form)
            print 'data={}'.format(data)
            for thisid in data:
                eventdb = Event.query.filter_by(id=thisid).one()

                # if we are generating a new version of the contract
                if form['addlaction'] == 'sendcontract':

                    # check appropriate fields are present for certain services
                    servicenames = set([s.service for s in eventdb.services])
                    if servicenames & {'coursemarking', 'finishline'}:
                        self._fielderrors = []
                        for field in ['race', 'date', 'mainStartTime', 'mainDistance' ]:
                            if not data[thisid][field]:
                                self._fielderrors.append({ 'name' : field, 'status' : 'please supply'})
                        ## handle select fields
                        for field in ['state', 'services', 'client', 'course']:
                            if not data[thisid][field]['id']:
                                self._fielderrors.append({ 'name' : '{}.id'.format(field), 'status' : 'please select'})
                        if self._fielderrors:
                            raise parameterError, 'missing fields'


                    # calculate service fees
                    servicefees = []

                    feetotal = 0
                    for service in eventdb.services:
                        servicefee = { 'service' : service.serviceLong }
                        # fixed fee
                        if service.feeType.feeType =='fixed':
                            thisfee = service.fee
                            servicefee['fee'] = thisfee
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
                                raise parameterError, 'cannot calculate fee if {} not set'.format(field)

                            feebasedons = FeeBasedOn.query.filter_by(serviceId=service.id).order_by(FeeBasedOn.fieldValue).all()
                            foundfee = False
                            for feebasedon in feebasedons:
                                lastfieldval = feebasedon.fieldValue
                                if debug: current_app.logger.debug('fieldval={} feebasedon.fieldValue={}'.format(fieldval, feebasedon.fieldValue))
                                if debug: current_app.logger.debug('type(fieldval)={} type(feebasedon.fieldValue)={}'.format(type(fieldval), type(feebasedon.fieldValue)))
                                if fieldval <= feebasedon.fieldValue:
                                    thisfee = feebasedon.fee
                                    servicefee['fee'] = thisfee
                                    servicefees.append( servicefee )
                                    foundfee = True
                                    break

                            # if fee not found, then set fielderrors appropriately
                            if not foundfee:
                                formfield = self.dbmapping[field]   # hopefully not a function
                                self._fielderrors = [{ 'name' : formfield, 'status' : 'cannot calculate fee if this is greater than {}'.format(lastfieldval) }]
                                raise ParameterError, 'cannot calculate fee if {} greater than {}'.format(field, lastfieldval)
                                
                        # fee is an add on
                        elif service.feeType.feeType =='addOn':
                            raise NotImplemented, 'addOn not implemented yet'
                        
                        # not sure how we could get here, but best to be defensive
                        else:
                            raise ParameterError, 'unknown feeType: {}'.format(service.feeType.feeType)

                        # accumulate total fee
                        feetotal += thisfee
                    
                    # generate contract
                    if debug: current_app.logger.debug('editor_method_posthook(): (before create()) eventdb.__dict__={}'.format(eventdb.__dict__))
                    docid = cm.create('{}-{}-{}.docx'.format(eventdb.client.client, eventdb.race.race, eventdb.date), eventdb, 
                                      addlfields={'servicenames': [s.service for s in eventdb.services],
                                                  'servicefees' : servicefees,
                                                  'event'       : eventdb.race.race,
                                                  'totalfees'   : { 'service' : 'TOTAL', 'fee' : feetotal },
                                                 })
                    
                    # update database to show contract sent
                    eventdb.state = State.query.filter_by(state=STATE_CONTRACT_SENT).one()
                    eventdb.contractSentDate = dt.dt2asc( date.today() )
                    eventdb.contractDocId = docid
                    
                    # find index with correct id and show database updates
                    for resprow in self._responsedata:
                        if resprow['rowid'] == thisid: 
                            resprow['state'] = { key:val for (key,val) in eventdb.state.__dict__.items() if key[0] != '_' }
                            resprow['contractSentDate'] = eventdb.contractSentDate
                            resprow['contractDocId'] = eventdb.contractDocId

                # if we are just resending current version of the contract
                else:
                    docid = eventdb.contractDocId

                # email sent depends on current state as this flows from 'sendcontract' and 'resendcontract'
                if eventdb.state.state == STATE_COMMITTED:
                    # prepare agreement accepted email 
                    templatestr = (db.session.query(Contract)
                                   .filter(Contract.contractTypeId==ContractType.id)
                                   .filter(ContractType.contractType=='race services')
                                   .filter(Contract.templateTypeId==TemplateType.id)
                                   .filter(TemplateType.templateType=='agreement accepted view')
                                   .one()
                                  ).block
                    template = Template( templatestr )
                    subject = 'ACCEPTED - FSRC Race Support Agreement: {} - {}'.format(eventdb.race.race, eventdb.date)

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
                    subject = 'FSRC Race Support Agreement: {} - {}'.format(eventdb.race.race, eventdb.date)

                # state must be STATE_COMMITTED or STATE_CONTRACT_SENT, else logic error
                else:
                    raise parameterError, 'editor_method_posthook(): bad state seen for {}: {}'.format(form['addlaction'], eventdb.state.state)

                # merge database fields into template and send email
                mergefields = deepcopy(eventdb.__dict__)
                mergefields['viewcontracturl'] = 'https://docs.google.com/document/d/{}/view'.format(docid)
                mergefields['downloadcontracturl'] = 'https://docs.google.com/document/d/{}/export?format=pdf'.format(docid)
                # need to bring in full path for email, so use url_root
                mergefields['acceptcontracturl'] = request.url_root[:-1] + url_for('frontend.acceptagreement', docid=docid)
                mergefields['servicenames'] = [s.service for s in eventdb.services] 
                mergefields['event'] = eventdb.race.race


                html = template.render( mergefields )
                tolist = eventdb.client.contactEmail
                cclist = current_app.config['CONTRACTS_CC']
                fromlist = current_app.config['CONTRACTS_CONTACT']
                sendmail( subject, fromlist, tolist, html, ccaddr=cclist )
