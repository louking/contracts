###########################################################################################
# sponsorscontract - handle contract management for race services contract
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/15/18        Lou King        Create
#
#   Copyright 2018 Lou King
###########################################################################################
'''
sponsorscontract - handle contract management for race services contract
===========================================================================
'''
# standard
from datetime import date, timedelta
from copy import deepcopy
from os.path import join as pathjoin

# pypi
from flask import current_app, url_for, request
from jinja2 import Template

# homegrown
from contracts.dbmodel import db, State, Sponsor, SponsorRaceDate, SponsorBenefit, SponsorLevel
from contracts.dbmodel import Contract, ContractType, TemplateType
from contracts.dbmodel import STATE_COMMITTED
from contracts.crudapi import DbCrudApiRolePermissions
from contracts.contractmanager import ContractManager
from contracts.mailer import sendmail
from loutilities.tables import get_request_data
from loutilities.timeu import asctime

dt = asctime('%Y-%m-%d')
humandt = asctime('%B %d, %Y')

class parameterError(Exception): pass

debug = True

###########################################################################################
class SponsorContract(DbCrudApiRolePermissions):
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
            cm = ContractManager(contractType='race sponsorship', 
                                 templateType='sponsor agreement', 
                                 driveFolderId=folderid,
                                 doctype='html',
                                 )

            # pull record(s) from database and save as flat dotted record
            data = get_request_data(form)
            print 'data={}'.format(data)
            for thisid in data:
                sponsordb = Sponsor.query.filter_by(id=thisid).one()
                racedate = SponsorRaceDate.query.filter_by(race_id=sponsordb.race.id, raceyear=sponsordb.raceyear).one()

                # bring in subrecords
                garbage = sponsordb.race
                garbage = sponsordb.client
                garbage = sponsordb.level

                # calculate the benefits (see https://stackoverflow.com/questions/40699642/how-to-query-many-to-many-sqlalchemy)
                benefitsdb = SponsorBenefit.query.join(SponsorBenefit.levels).filter(SponsorLevel.id == sponsordb.level.id).order_by(SponsorBenefit.order).all()
                benefits = [b.benefit for b in benefitsdb]

                # get coupon date for agreement and email
                # TODO: retrieve from database
                coupondate = humandt.dt2asc(dt.asc2dt(racedate.racedate) - timedelta(3))
                ncoupons = sponsordb.level.couponcount
                wcoupons = 'zero one two three four five six seven eight nine'.split()[ncoupons]
                couponcount = '{} ({})'.format(wcoupons, ncoupons) if ncoupons else None

                # if we are generating a new version of the contract
                if form['addlaction'] == 'sendcontract':

                    # generate contract
                    if debug: current_app.logger.debug('editor_method_posthook(): (before create()) sponsordb.__dict__={}'.format(sponsordb.__dict__))
                    docid = cm.create('{} {} {} Sponsor Agreement'.format(
                                        sponsordb.raceyear, sponsordb.race.raceshort, sponsordb.client.client
                                      ), 
                                      sponsordb, 
                                      addlfields={
                                                  '_date_'            : humandt.dt2asc(date.today()),
                                                  '_racedate_'        : humandt.dt2asc(dt.asc2dt(racedate.racedate)),
                                                  '_rdcertlogo_'      : pathjoin(current_app.static_folder, 'rd-cert-logo.png'),
                                                  '_raceheader_'      : '<img src="{}" width=6in>'.format(pathjoin(current_app.static_folder, 
                                                                            '{}-header.png'.format(sponsordb.race.raceshort.lower()))),
                                                  '_benefits_'        : benefits,
                                                  '_raceloc_'         : 'XXX race loc config XXX',
                                                  '_racebeneficiary_' : 'XXX race beneficiary config XXX',
                                                  '_coupondate_'      : coupondate,
                                                  '_couponcount_'     : couponcount.capitalize(), # ok to assume first word in sentence
                                                 })
                    
                    # update database to show contract sent/agreed
                    sponsordb.state = State.query.filter_by(state=STATE_COMMITTED).one()
                    sponsordb.dateagreed = dt.dt2asc( date.today() )
                    sponsordb.contractDocId = docid
                    
                    # find index with correct id and show database updates
                    for resprow in self._responsedata:
                        if resprow['rowid'] == thisid: 
                            resprow['state'] = { key:val for (key,val) in sponsordb.state.__dict__.items() if key[0] != '_' }
                            resprow['dateagreed'] = sponsordb.dateagreed
                            resprow['contractDocId'] = sponsordb.contractDocId

                # if we are just resending current version of the contract
                else:
                    docid = sponsordb.contractDocId

                # prepare agreement email (new contract or resending)
                templatestr = (db.session.query(Contract)
                               .filter(Contract.contractTypeId==ContractType.id)
                               .filter(ContractType.contractType=='race sponsorship')
                               .filter(Contract.templateTypeId==TemplateType.id)
                               .filter(TemplateType.templateType=='sponsor email')
                               .one()
                              ).block
                template = Template( templatestr )
                subject = '{} Sponsorship Agreement for {}'.format(sponsordb.race.race, sponsordb.client.client)

                # bring in subrecords
                garbage = sponsordb.race

                # merge database fields into template and send email
                mergefields = deepcopy(sponsordb.__dict__)
                mergefields['viewcontracturl'] = 'https://docs.google.com/document/d/{}/view'.format(docid)
                mergefields['downloadcontracturl'] = 'https://docs.google.com/document/d/{}/export?format=pdf'.format(docid)
                # need to bring in full path for email, so use url_root
                # mergefields['_race_'] = sponsordb.race.race
                racedate = SponsorRaceDate.query.filter_by(race_id=sponsordb.race.id, raceyear=sponsordb.raceyear).one()
                mergefields['_racedate_'] = humandt.dt2asc(dt.asc2dt(racedate.racedate))
                mergefields['_coupondate_'] = coupondate
                mergefields['_couponcount_'] = couponcount


                html = template.render( mergefields )
                tolist = sponsordb.client.contactEmail
                rdemail = '{} <{}>'.format(sponsordb.race.racedirector, sponsordb.race.rdemail)
                cclist = current_app.config['SPONSORSHIPQUERY_CC'] + [rdemail]
                fromlist = '{} <{}>'.format(sponsordb.race.race, current_app.config['SPONSORSHIPQUERY_CONTACT'])
                sendmail( subject, fromlist, tolist, html, ccaddr=cclist )
