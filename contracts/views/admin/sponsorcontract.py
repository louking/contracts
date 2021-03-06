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
from contracts.dbmodel import SponsorRaceVbl
from contracts.dbmodel import Contract, ContractType, TemplateType
from contracts.dbmodel import STATE_COMMITTED
from contracts.contractmanager import ContractManager
from contracts.mailer import sendmail
from contracts.runsignup import RunSignUp
from contracts.trends import calculateTrend

from loutilities.tables import DbCrudApiRolePermissions, get_request_data
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

        # someday we might allow multiple records to be processed in a single request

        # pull record(s) from database and save as flat dotted record
        data = get_request_data(form)
        for thisid in data:
            sponsordb = Sponsor.query.filter_by(id=thisid).one_or_none()

            # if we're creating, we just flushed the row, but the id in the form was 0
            # retrieve the created row through saved id
            if not sponsordb:
                thisid = self.created_id
                sponsordb = Sponsor.query.filter_by(id=thisid).one()

            # the following can be true only for put() [edit] method
            if 'addlaction' in form and form['addlaction'] in ['sendcontract', 'resendcontract']:
                folderid = current_app.config['CONTRACTS_DB_FOLDER']

                # need an instance of contract manager to take care of saving the contract
                cm = ContractManager(contractType='race sponsorship', 
                                     templateType='sponsor agreement', 
                                     driveFolderId=folderid,
                                     doctype='html',
                                     )

                racedate = SponsorRaceDate.query.filter_by(race_id=sponsordb.race.id, raceyear=sponsordb.raceyear).one()

                # bring in subrecords
                garbage = sponsordb.race
                garbage = sponsordb.client
                garbage = sponsordb.level

                # calculate the benefits (see https://stackoverflow.com/questions/40699642/how-to-query-many-to-many-sqlalchemy)
                benefitsdb = SponsorBenefit.query.join(SponsorBenefit.levels).filter(SponsorLevel.id == sponsordb.level.id).order_by(SponsorBenefit.order).all()
                benefits = [b.benefit for b in benefitsdb]

                # calculate display for coupon count. word (num) if less than 10, otherwise num
                # but note there may not be a coupon count
                # ccouponcount is capitalized
                ncoupons = sponsordb.level.couponcount
                if ncoupons:
                    if ncoupons < 10:
                        wcoupons = 'zero one two three four five six seven eight nine'.split()[ncoupons]
                        couponcount = '{} ({})'.format(wcoupons, ncoupons) if ncoupons else None
                    else:
                        couponcount = str(ncoupons)
                    ccouponcount = couponcount.capitalize()
                else:
                    couponcount = None
                    ccouponcount = None

                # pick up variables
                variablesdb = SponsorRaceVbl.query.filter_by(race_id=sponsordb.race.id).all()
                variables = {v.variable:v.value for v in variablesdb}

                # if we are generating a new version of the contract
                if form['addlaction'] == 'sendcontract':

                    # set up dateagreed, if not already there
                    if not sponsordb.dateagreed:
                        sponsordb.dateagreed = dt.dt2asc( date.today() )


                    # additional fields for contract
                    addlfields={
                                      '_date_'            : humandt.dt2asc(dt.asc2dt(sponsordb.dateagreed)),
                                      '_racedate_'        : humandt.dt2asc(dt.asc2dt(racedate.racedate)),
                                      '_rdcertlogo_'      : pathjoin(current_app.static_folder, 'rd-cert-logo.png'),
                                      '_raceheader_'      : '<img src="{}" width=6in>'.format(pathjoin(current_app.static_folder, 
                                                                '{}-header.png'.format(sponsordb.race.raceshort.lower()))),
                                      '_benefits_'        : benefits,
                                      '_raceloc_'         : racedate.raceloc,
                                      '_racebeneficiary_' : racedate.beneficiary,
                                      '_couponcount_'     : ccouponcount, # ok to assume this is first word in sentence
                                     }
                    addlfields.update(variables)

                    # generate contract
                    if debug: current_app.logger.debug('editor_method_posthook(): (before create()) sponsordb.__dict__={}'.format(sponsordb.__dict__))
                    docid = cm.create('{} {} {} Sponsor Agreement'.format(
                                        sponsordb.raceyear, sponsordb.race.raceshort, sponsordb.client.client
                                      ), 
                                      sponsordb, 
                                      addlfields=addlfields,
                                     )
                    
                    # update database to show contract sent/agreed
                    sponsordb.state = State.query.filter_by(state=STATE_COMMITTED).one()
                    sponsordb.contractDocId = docid
                    
                    # find index with correct id and show database updates
                    for resprow in self._responsedata:
                        if resprow['rowid'] == thisid: 
                            resprow['state'] = { key:val for (key,val) in list(sponsordb.state.__dict__.items()) if key[0] != '_' }
                            resprow['dateagreed'] = sponsordb.dateagreed
                            resprow['contractDocId'] = sponsordb.contractDocId

                    # configure coupon provider with coupon code (supported providers)
                    if sponsordb.race.couponprovider and sponsordb.level.couponcount and sponsordb.level.couponcount > 0:
                        expiration = racedate.racedate
                        numregistrations = sponsordb.level.couponcount
                        clientname = sponsordb.client.client
                        raceid = sponsordb.race.couponproviderid
                        couponcode = sponsordb.couponcode
                        start = sponsordb.dateagreed
                        if sponsordb.race.couponprovider.lower() == 'runsignup':
                            with RunSignUp(key=current_app.config['RSU_KEY'], secret=current_app.config['RSU_SECRET'], debug=debug) as rsu:
                                coupons = rsu.getcoupons(raceid, couponcode)
                                if coupons:
                                    coupon = coupons[-1]     # should be only one entry, but last is the current one (?)
                                    coupon_id = coupon['coupon_id']
                                    # override start with the date portion of start_date
                                    start = coupon['start_date'].split(' ')[0]
                                else:
                                    coupon_id = None
                                rsu.setcoupon(raceid, couponcode, start, expiration, numregistrations, clientname, coupon_id=coupon_id)

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
                mergefields['_coupondate_'] = variables['_coupondate_']
                mergefields['_couponcount_'] = couponcount


                html = template.render( mergefields )
                tolist = sponsordb.client.contactEmail
                rdemail = '{} <{}>'.format(sponsordb.race.racedirector, sponsordb.race.rdemail)
                cclist = current_app.config['SPONSORSHIPAGREEMENT_CC'] + [rdemail]
                fromlist = '{} <{}>'.format(sponsordb.race.race, current_app.config['SPONSORSHIPQUERY_CONTACT'])
                sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

            # calculate and update trend
            calculateTrend(sponsordb)
            # kludge to force response data to have correct trend
            # TODO: remove when #245 fixed
            thisndx = [i['rowid'] for i in self._responsedata].index(thisid)
            self._responsedata[thisndx]['trend'] = sponsordb.trend