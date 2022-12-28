'''
sponsorscontract - handle contract management for race services contract
===========================================================================
'''
# standard
from datetime import date
from copy import deepcopy
from os.path import join as pathjoin

# pypi
from flask import current_app, flash
from jinja2 import Template

# homegrown
from contracts.dbmodel import db, State, Sponsor, SponsorRaceDate, SponsorBenefit, SponsorLevel
from contracts.dbmodel import SponsorRaceVbl
from contracts.dbmodel import Contract, ContractType, TemplateType
from contracts.dbmodel import STATE_COMMITTED
from ...trends import check_sponsorship_conflicts, render_sponsorship_conflicts
from contracts.contractmanager import ContractManager
from loutilities.flask_helpers.mailer import sendmail
from contracts.runsignup import RunSignUp
from contracts.trends import calculateTrend

from loutilities.tables import DbCrudApiRolePermissions, get_request_data
from loutilities.timeu import asctime

dt = asctime('%Y-%m-%d')
humandt = asctime('%B %d, %Y')

class parameterError(Exception): pass

debug = True

class SponsorContract(DbCrudApiRolePermissions):
    '''
    extend DbCrudApiRolePermissions to handle send contract request within put() [edit] method
    '''
    
    def open(self):
        super().open()

        # flag any errors found after copying then resetting self.rows
        # NOTE: this assumes SponsorContract is instantiated as a client table (i.e., not serverside)
        theserows = list(self.rows)
        self.rows = iter(theserows)
        error_list = check_sponsorship_conflicts(theserows)
        if error_list:
            flash(render_sponsorship_conflicts(error_list))

    def editor_method_posthook(self, form):
        '''
        send contract to client contact if asked to do so, after processing put()

        note row has already been committed to the database, so can be retrieved
        '''

        # someday we might allow multiple records to be processed in a single request
        # NOTE: logic added to support updating multiple row trend field might break multiple record handling

        # set up to check to see if any errors introduced
        error_list = []
        
        # set up to track additional responses
        rowids = [i['rowid'] for i in self._responsedata]
        
        # pull record(s) from database and save as flat dotted record
        data = get_request_data(form)
        for thisid in data:
            thissponsorship = Sponsor.query.filter_by(id=thisid).one_or_none()

            # if we're creating, we just flushed the row, but the id in the form was 0
            # retrieve the created row through saved id
            if not thissponsorship:
                thisid = self.created_id
                thissponsorship = Sponsor.query.filter_by(id=thisid).one()

            # the following can be true only for put() [edit] method
            if 'addlaction' in form and form['addlaction'] in ['sendcontract', 'resendcontract']:
                folderid = current_app.config['CONTRACTS_DB_FOLDER']

                # need an instance of contract manager to take care of saving the contract
                cm = ContractManager(contractType='race sponsorship', 
                                     templateType='sponsor agreement', 
                                     driveFolderId=folderid,
                                     doctype='html',
                                     )

                racedate = SponsorRaceDate.query.filter_by(race_id=thissponsorship.race.id, raceyear=thissponsorship.raceyear).one()

                # bring in subrecords
                garbage = thissponsorship.race
                garbage = thissponsorship.client
                garbage = thissponsorship.level

                # calculate the benefits (see https://stackoverflow.com/questions/40699642/how-to-query-many-to-many-sqlalchemy)
                benefitsdb = SponsorBenefit.query.join(SponsorBenefit.levels).filter(SponsorLevel.id == thissponsorship.level.id).order_by(SponsorBenefit.order).all()
                benefits = [b.benefit for b in benefitsdb]

                # calculate display for coupon count. word (num) if less than 10, otherwise num
                # but note there may not be a coupon count
                # ccouponcount is capitalized
                ncoupons = thissponsorship.level.couponcount
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
                variablesdb = SponsorRaceVbl.query.filter_by(race_id=thissponsorship.race.id).all()
                variables = {v.variable:v.value for v in variablesdb}

                # if we are generating a new version of the contract
                if form['addlaction'] == 'sendcontract':

                    # set up dateagreed, if not already there
                    if not thissponsorship.dateagreed:
                        thissponsorship.dateagreed = dt.dt2asc( date.today() )


                    # additional fields for contract
                    addlfields={
                                      '_date_'            : humandt.dt2asc(dt.asc2dt(thissponsorship.dateagreed)),
                                      '_racedate_'        : humandt.dt2asc(dt.asc2dt(racedate.racedate)),
                                      '_rdcertlogo_'      : pathjoin(current_app.static_folder, 'rd-cert-logo.png'),
                                      '_raceheader_'      : '<img src="{}" width=6in>'.format(pathjoin(current_app.static_folder, 
                                                                '{}-header.png'.format(thissponsorship.race.raceshort.lower()))),
                                      '_benefits_'        : benefits,
                                      '_raceloc_'         : racedate.raceloc,
                                      '_racebeneficiary_' : racedate.beneficiary,
                                      '_couponcount_'     : ccouponcount, # ok to assume this is first word in sentence
                                     }
                    addlfields.update(variables)

                    # generate contract
                    if debug: current_app.logger.debug('editor_method_posthook(): (before create()) sponsordb.__dict__={}'.format(thissponsorship.__dict__))
                    docid = cm.create('{} {} {} Sponsor Agreement'.format(
                                        thissponsorship.raceyear, thissponsorship.race.raceshort, thissponsorship.client.client
                                      ), 
                                      thissponsorship, 
                                      addlfields=addlfields,
                                     )
                    
                    # update database to show contract sent/agreed
                    thissponsorship.state = State.query.filter_by(state=STATE_COMMITTED).one()
                    thissponsorship.contractDocId = docid
                    
                    # find index with correct id and show database updates
                    for resprow in self._responsedata:
                        if resprow['rowid'] == thisid: 
                            resprow['state'] = { key:val for (key,val) in list(thissponsorship.state.__dict__.items()) if key[0] != '_' }
                            resprow['dateagreed'] = thissponsorship.dateagreed
                            resprow['contractDocId'] = thissponsorship.contractDocId

                    # configure coupon provider with coupon code (supported providers)
                    if thissponsorship.race.couponprovider and thissponsorship.level.couponcount and thissponsorship.level.couponcount > 0:
                        expiration = racedate.racedate
                        numregistrations = thissponsorship.level.couponcount
                        clientname = thissponsorship.client.client
                        raceid = thissponsorship.race.couponproviderid
                        couponcode = thissponsorship.couponcode
                        start = thissponsorship.dateagreed
                        if thissponsorship.race.couponprovider.lower() == 'runsignup':
                            with RunSignUp(key=current_app.config['RSU_KEY'], secret=current_app.config['RSU_SECRET'], debug=debug) as rsu:
                                coupons = rsu.getcoupons(raceid, couponcode)
                                # rsu search includes any coupons with the couponcode with the coupon string, so we need to filter
                                coupons = [c for c in coupons if c['coupon_code']==couponcode]
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
                    docid = thissponsorship.contractDocId


                # prepare agreement email (new contract or resending)
                templatestr = (db.session.query(Contract)
                               .filter(Contract.contractTypeId==ContractType.id)
                               .filter(ContractType.contractType=='race sponsorship')
                               .filter(Contract.templateTypeId==TemplateType.id)
                               .filter(TemplateType.templateType=='sponsor email')
                               .one()
                              ).block
                template = Template( templatestr )
                subject = '{} Sponsorship Agreement for {}'.format(thissponsorship.race.race, thissponsorship.client.client)

                # bring in subrecords
                garbage = thissponsorship.race

                # merge database fields into template and send email
                mergefields = deepcopy(thissponsorship.__dict__)
                mergefields['viewcontracturl'] = 'https://docs.google.com/document/d/{}/view'.format(docid)
                mergefields['downloadcontracturl'] = 'https://docs.google.com/document/d/{}/export?format=pdf'.format(docid)
                # need to bring in full path for email, so use url_root
                # mergefields['_race_'] = sponsordb.race.race
                racedate = SponsorRaceDate.query.filter_by(race_id=thissponsorship.race.id, raceyear=thissponsorship.raceyear).one()
                mergefields['_racedate_'] = humandt.dt2asc(dt.asc2dt(racedate.racedate))
                mergefields['_coupondate_'] = variables['_coupondate_']
                mergefields['_couponcount_'] = couponcount

                html = template.render( mergefields )
                tolist = thissponsorship.client.contactEmail
                rdemail = '{} <{}>'.format(thissponsorship.race.racedirector, thissponsorship.race.rdemail)
                cclist = current_app.config['SPONSORSHIPAGREEMENT_CC'] + [rdemail]
                fromlist = '{} <{}>'.format(thissponsorship.race.race, current_app.config['SPONSORSHIPQUERY_CONTACT'])
                sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

            # retrieve all sponsor records for this raceyear, race, client having this state
            # TODO: if this introduces a state inconsistency, other records for raceyear, race, client now have incorrect trend
            thesesponsorships = Sponsor.query.filter_by(
                raceyear=thissponsorship.raceyear, 
                race=thissponsorship.race,
                client=thissponsorship.client,
                state=thissponsorship.state,
            ).all()
            
            # calculate and update trend for all sponsor records for this raceyear, race, client
            calculateTrend(thesesponsorships)
            
            # kludge to force response data to have correct trend
            # TODO: remove when #245 fixed
            thisndx = rowids.index(thisid)
            self._responsedata[thisndx]['trend'] = thissponsorship.trend
            
            # update trend for records not originally asked for
            for sship in [s for s in thesesponsorships if s.id not in rowids]:
                self._responsedata.append({'rowid': sship.id, 'trend': thissponsorship.trend})
                rowids.append(sship.id)
            
            # check for inconsistent sponsorships for this year/race/client
            # check if there were any state inconsistencies introduced
            error_list += check_sponsorship_conflicts(thesesponsorships)
        
        # flag any errors introduced
        if error_list:
            self.responsekeys['popup'] = render_sponsorship_conflicts(error_list)

