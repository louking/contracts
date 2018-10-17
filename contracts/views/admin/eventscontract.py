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
from contracts.dbmodel import db, Event, State
from contracts.crudapi import DbCrudApiRolePermissions
from contracts.contractmanager import ContractManager
from loutilities.tables import get_request_data
from loutilities.timeu import asctime

dt = asctime('%Y-%m-%d')

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

                    # generate contract
                    docid = cm.create('{}-{}.docx'.format(eventdb.client.client, eventdb.date), eventdb)
                    
                    # update database to show contract sent
                    eventdb.state = State.query.filter_by(state='contract-sent').one()
                    eventdb.contractSentDate = dt.dt2asc( date.today() )
                    
                    # find index with correct id and show database updates
                    for resprow in self._responsedata:
                        if resprow['rowid'] == thisid: 
                            resprow['state'] = { key:val for (key,val) in eventdb.state.__dict__.items() if key[0] != '_' }
                            resprow['contractSentDate'] = eventdb.contractSentDate

                # TODO: send contract mail to client