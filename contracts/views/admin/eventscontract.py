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

# pypi
from flask import current_app

# homegrown
from contracts.dbmodel import db, Event, State, FeeBasedOn
from contracts.crudapi import DbCrudApiRolePermissions
from contracts.contractmanager import ContractManager
from loutilities.tables import get_request_data
from loutilities.timeu import asctime

dt = asctime('%Y-%m-%d')

class ParameterError(Exception): pass

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
        if 'addlaction' in form and form['addlaction'] == 'sendcontract':
            folderid = current_app.config['CONTRACTS_DB_FOLDER']

            # need an instance of contract manager to take care of saving the contract
            cm = ContractManager(contractType='race services', driveFolderId=folderid)

            # pull record(s) from database and save as flat dotted record
            data = get_request_data(form)
            for thisid in data:
                eventdb = Event.query.filter_by(id=thisid).one()

                # check state to see if we are generating a new version or just sending current version
                if not eventdb.state or eventdb.state.state not in ['contract-sent', 'committed']:

                    # TODO: calculate service fees
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
                            fieldval = int(getattr(eventdb, field))

                            # field not set, then set self._fielderrors appropriately
                            if not fieldval:
                                formfield = self.dbmapping[field]   # hopefully not a function
                                self._fielderrors = [{ 'name' : formfield, 'status' : 'needed to calculate fee' }]
                                raise ParameterError, 'cannot calculate fee if {} not set'.format(field)

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
                    docid = cm.create('{}-{}-{}.docx'.format(eventdb.client.client, eventdb.event, eventdb.date), eventdb, 
                                      addlfields={'servicenames': [s.service for s in eventdb.services],
                                                  'servicefees' : servicefees,
                                                  'totalfees' : { 'service' : 'TOTAL', 'fee' : feetotal },
                                                 })
                    
                    # update database to show contract sent
                    eventdb.state = State.query.filter_by(state='contract-sent').one()
                    eventdb.contractSentDate = dt.dt2asc( date.today() )
                    eventdb.contractDocId = docid
                    
                    # find index with correct id and show database updates
                    for resprow in self._responsedata:
                        if resprow['rowid'] == thisid: 
                            resprow['state'] = { key:val for (key,val) in eventdb.state.__dict__.items() if key[0] != '_' }
                            resprow['contractSentDate'] = eventdb.contractSentDate
                            resprow['contractDocId'] = eventdb.contractDocId

                # TODO: send contract mail to client