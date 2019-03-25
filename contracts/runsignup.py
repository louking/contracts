###########################################################################################
#   runsignup - access methods for runsignup.com
#
#   Date        Author      Reason
#   ----        ------      ------
#   02/19/19    Lou King    Create from loutilities.runsignup
#
#   Copyright 2019 Lou King
###########################################################################################
'''
runsignup - access methods for runsignup.com
===================================================
'''

# standard
import logging
from json import dumps

# pypi
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

# github

# other

# home grown

# login API (deprecated)
login_url = 'https://runsignup.com/rest/login'
logout_url = 'https://runsignup.com/rest/logout'
coupons_url = 'https://runsignup.com/rest/race/{race_id}/coupons'

class accessError(Exception): pass
class parameterError(Exception): pass

thislogger = logging.getLogger("contracts.runsignup")

########################################################################
class RunSignUp():
########################################################################
    '''
    access methods for RunSignUp.com

    either key and secret OR email and password should be supplied
    key and secret take precedence

    :param key: key from runsignup (direct key, no OAuth)
    :param secret: secret from runsignup (direct secret, no OAuth)
    :param email: email for use by Login API (deprecated)
    :param password: password for use by Login API (deprecated)
    :param debug: set to True for debug logging of http requests, default False
    '''

    #----------------------------------------------------------------------
    def __init__(self, key=None, secret=None, email=None, password=None, debug=False):
    #----------------------------------------------------------------------
        """
        initialize
        """

        # does user want to debug?
        logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
        if debug:
            # set up debug logging
            thislogger.setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        else:
            # turn off debug logging
            thislogger.setLevel(logging.NOTSET)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.NOTSET)
            requests_log.propagate = False

        if (not key and not email):
            raise parameterError, 'either key/secret or email/password must be supplied'
        if (key and not secret) or (secret and not key):
            raise parameterError, 'key and secret must be supplied together'
        if (email and not password) or (password and not email):
            raise parameterError, 'email and password must be supplied together'

        self.key = key
        self.secret = secret
        self.email = email
        self.password = password
        self.debug = debug
        self.client_credentials = {}
        if key:
            self.credentials_type = 'key'
        else:
            self.credentials_type = 'login'

    #----------------------------------------------------------------------
    def __enter__(self):
    #----------------------------------------------------------------------
        self.open()
        return self

    #----------------------------------------------------------------------
    def __exit__(self, exc_type, exc_value, traceback):
    #----------------------------------------------------------------------
        self.close()

    #----------------------------------------------------------------------
    def open(self):
    #----------------------------------------------------------------------

        # set up session for multiple requests
        self.session = requests.Session()

        # key / secret supplied - this take precedence
        if self.credentials_type == 'key':
            self.client_credentials = {'api_key'    : self.key,
                                       'api_secret' : self.secret}

        # email / password supplied
        else:     
            # login to runsignup - note temporary keys will expire 1 hour after last API call
            # see https://runsignup.com/API/login/POST
            r = requests.post(login_url, params={'format' : 'json'}, data={'email' : self.email, 'password' : self.password})
            resp = r.json()

            self.credentials_type = 'login'
            self.client_credentials = {'tmp_key'    : resp['tmp_key'],
                                       'tmp_secret' : resp['tmp_secret']}

    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        close down
        '''
        self.client_credentials = {}
        self.session.close()

        # TODO: should we also log out?


    #----------------------------------------------------------------------
    def getcoupons(self, race_id, coupon_code=None):
    #----------------------------------------------------------------------
        """
        return coupons accessible to this application

        :param race_id: id of race
        :param coupon_code: coupon code for specific coupon, None for all coupons
        """
        
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
                    "discount_type": "E",
                    # TODO: should there be an argument with startdate?
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
        

    #----------------------------------------------------------------------
    def _rsuget(self, methodurl, **payload):
    #----------------------------------------------------------------------
        """
        get method for runsignup access
        
        :param methodurl: runsignup method url to call
        :param contentfield: content field to retrieve from response
        :param **payload: parameters for the method
        """
        
        thispayload = self.client_credentials.copy()
        thispayload.update(payload)
        thispayload.update({
            'format':'json',
            'request_format':'json',
        })

        resp = self.session.get(methodurl, params=thispayload)
        if resp.status_code != 200:
            raise accessError, 'HTTP response code={}, url={}'.format(resp.status_code,resp.url)

        data = resp.json()

        if 'error' in data:
            raise accessError, 'RSU response code={}-{}, url={}'.format(data['error']['error_code'],data['error']['error_msg'],resp.url)
    
        return data 
        
    #----------------------------------------------------------------------
    def _rsupost(self, methodurl, **data):
    #----------------------------------------------------------------------
        """
        get method for runsignup access
        
        :param methodurl: runsignup method url to call
        :param contentfield: content field to retrieve from response
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
            raise accessError, 'HTTP response code={}, url={}'.format(resp.status_code,resp.url)

        data = resp.json()

        if 'error' in data:
            raise accessError, 'RSU response code={}-{}, url={}'.format(data['error']['error_code'],data['error']['error_msg'],resp.url)
    
        return data 
        
