###########################################################################################
#   runsignup - access methods for runsignup.com
#
#   Date        Author      Reason
#   ----        ------      ------
#   02/19/19    Lou King    Create from loutilities.runsignup
#   07/30/26    Lou King    refactor to use running.runsignup.RunSignupBase for shared auth/session handling
#
#   Copyright 2019 Lou King
###########################################################################################
'''
runsignup - access methods for runsignup.com
===================================================
'''

# standard
from json import dumps

# pypi
from flask import current_app

# github

# other

# home grown
from running.runsignup import RunSignupBase, accessError

# use api.runsignup.com per https://info.runsignup.com/2025/08/06/upgrading-our-api-infrastructure-for-ai-api-runsignup-com/
coupons_url = 'https://api.runsignup.com/rest/race/{race_id}/coupons'
race_url = 'https://api.runsignup.com/rest/race/{race_id}'
raceparticipants_url = 'https://api.runsignup.com/rest/race/{race_id}/participants'
removedparticipants_url = 'https://api.runsignup.com/rest/race/{race_id}/removed-participants'

########################################################################
class RunSignUp(RunSignupBase):
########################################################################
    '''
    access methods for RunSignUp.com

    see :class:`running.runsignup.RunSignupBase` for authentication / session parameters
    '''

    #----------------------------------------------------------------------
    def getcoupons(self, race_id, coupon_code=None):
    #----------------------------------------------------------------------
        """
        return coupons accessible to this application

        :param race_id: id of race
        :param coupon_code: coupon code for specific coupon, None for all coupons
        """

        if self.debug:
            current_app.logger.debug('getcoupons({}, coupon_code={})'.format(race_id, coupon_code))

        # max number of coupons in coupon list is 100, so need to loop, collecting
        # BITESIZE coupons at a time.  These are all added to coupons list, and final
        # list is returned to the caller
        BITESIZE = 100
        page = 1
        coupons = []
        while True:
            params = {
                'page':page,
                'results_per_page':BITESIZE,
            }
            if coupon_code:
                params['coupon_code'] = coupon_code

            data = self._rsuget(coupons_url.format(race_id=race_id),
                                **params
                               )
            if len(data['coupons']) == 0: break

            thesecoupons = data['coupons']

            coupons += thesecoupons
            page += 1

            # stop iterating if we've reached the end of the data
            if len(data['coupons']) < BITESIZE: break

        return coupons

    #----------------------------------------------------------------------
    def setcoupon(self, race_id, coupon_code, start, expiration, numregistrations, clientname, coupon_id=None):
    #----------------------------------------------------------------------
        """
        add or edit coupon


        :param race_id: id of race
        :param coupon_code: coupon code for specific coupon to add or edit
        :param start: start date in yyyy-mm-dd format
        :param expiration: expiration date in yyyy-mm-dd format
        :param numregistrations: number of registrations this coupon is good for
        :param clientname: client name for notes
        :param coupon_id: optional coupon_id for edit, None for add
        """

        if self.debug:
            current_app.logger.debug('setcoupon({}, {}, {}, {}, {}, {}, coupon_id={})'.format(
                        race_id, coupon_code, start, expiration, numregistrations, clientname, coupon_id))

        params = {
            'race_id'           : race_id,
            'request_format'    : 'json',
        }
        request = {
            'coupons' : [
                {
                    "coupon_id": coupon_id,
                    "coupon_code": coupon_code,
                    "percentage": 100,
                    "fixed_discount_in_cents": 0,
                    "discount_type": "R",
                    "start_date": "{} 00:00:00".format(start),
                    "end_date": "{} 23:59:59".format(expiration),

                    "applies_to_race_fee": "T",
                    "exclude_event_cost": "F",
                    "applies_to_giveaway": "F",
                    "applies_to_addons": "F",
                    "applies_to_club_membership_discounts": "F",
                    "applies_to_race_memberships": "F",
                    "applies_to_group_setup_fees": "F",
                    "applies_to_group_special_event_costs": "F",
                    "applies_to_age_based_pricing": "F",
                    "applies_to_multi_person_pricing": "F",
                    "applies_to_extra_fee": "F",
                    "applies_with_multi_event_discount": "F",
                    "applies_to_store": "F",

                    "new_customer_only": "F",
                    "minimum_amount_in_cents": 0,
                    "max_num_race_registrants": numregistrations,

                    "event_specific": "F",
                    "applicable_event_ids": [],

                    "coupon_notes": clientname,
                    "tags": [],
                }
            ]
        }
        request_json = dumps(request)
        params['request'] = request_json

        data = self._rsupost(coupons_url.format(race_id=race_id),
                            **params
                           )

        return data['coupons']


    # ----------------------------------------------------------------------
    def getraceevents(self, race_id):
    # ----------------------------------------------------------------------
        """
        return events for race information accessible to this application
        uses get race RSU method

        :param race_id: id of race
        """

        if self.debug:
            current_app.logger.debug('getraceevents({})'.format(race_id))

        data = self._rsuget(race_url.format(race_id=race_id),
                            )
        events = data['race']['events']

        return events


    # ----------------------------------------------------------------------
    def getraceparticipants(self, race_id, event_id, **kwargs):
    # ----------------------------------------------------------------------
        """
        return race information accessible to this application

        :param race_id: id of race
        :param event_id: id of event (instance of event for race in a given year)
        """

        if self.debug:
            current_app.logger.debug('getraceparticipants({}, event_id={})'.format(race_id, event_id))

        # max number of raceparticipants in raceparticipant list is 100, so need to loop, collecting
        # BITESIZE raceparticipants at a time.  These are all added to raceparticipants list, and final
        # list is returned to the caller
        BITESIZE = 100
        page = 1
        raceparticipants = []
        while True:
            params = {
                'event_id': event_id,
                'page': page,
                'results_per_page': BITESIZE,
            }
            params.update(**kwargs)

            # note list is returned; only asking for one event, so data gets the first item in list
            data = self._rsuget(raceparticipants_url.format(race_id=race_id),
                                **params
                                )[0]
            if 'participants' not in data or len(data['participants']) == 0: break

            theseraceparticipants = data['participants']

            raceparticipants += theseraceparticipants
            page += 1

            # stop iterating if we've reached the end of the data
            if len(data['participants']) < BITESIZE: break

        return raceparticipants

    # ----------------------------------------------------------------------
    def getremovedparticipants(self, race_id, event_id, **kwargs):
    # ----------------------------------------------------------------------
        """
        return race information accessible to this application

        :param race_id: id of race
        :param event_id: id of event (instance of event for race in a given year)
        """

        if self.debug:
            current_app.logger.debug('getremovedparticipants({}, event_id={})'.format(race_id, event_id))

        # max number of raceparticipants in raceparticipant list is 100, so need to loop, collecting
        # BITESIZE raceparticipants at a time.  These are all added to raceparticipants list, and final
        # list is returned to the caller
        BITESIZE = 100
        page = 1
        removedparticipants = []
        while True:
            params = {
                'event_id': event_id,
                'page': page,
                'results_per_page': BITESIZE,
            }
            params.update(**kwargs)

            # note list is returned; only asking for one event, so data gets the first item in list
            data = self._rsuget(removedparticipants_url.format(race_id=race_id),
                                **params
                                )[0]
            if 'event' not in data: break
            if 'participants' not in data['event'] or len(data['event']['participants']) == 0: break

            theseremovedparticipants = data['event']['participants']

            removedparticipants += theseremovedparticipants
            page += 1

            # stop iterating if we've reached the end of the data
            if len(data['event']['participants']) < BITESIZE: break

        return removedparticipants

    #----------------------------------------------------------------------
    def _rsupost(self, methodurl, **data):
    #----------------------------------------------------------------------
        """
        post method for runsignup access

        RunSignupBase only implements _rsuget/_rsugetcsv; contracts needs POST for coupon management

        :param methodurl: runsignup method url to call
        :param **data: parameters for the method
        """

        thispayload = self.client_credentials.copy()
        thispayload.update(data)
        thispayload.update({
            'format':'json',
            'request_format':'json',
        })

        resp = self.session.post(methodurl, data=thispayload)
        if resp.status_code != 200:
            raise accessError('HTTP response code={}, url={}'.format(resp.status_code,resp.url))

        data = resp.json()

        if 'error' in data:
            raise accessError('RSU response code={}-{}, url={}'.format(data['error']['error_code'],data['error']['error_msg'],resp.url))

        return data

