'''
helpers - commonly needed utilities
====================================================================================
'''

# standard

# pypi
from flask import g, current_app

# homegrown
from .dbmodel import LocalInterest
from .runsignup import RunSignUp
from loutilities.user.model import Interest

def localinterest():
    interest = Interest.query.filter_by(interest=g.interest).one()
    return LocalInterest.query.filter_by(interest_id=interest.id).one()

def make_runsignup_client(**kwargs):
    '''
    create a contracts.runsignup.RunSignUp client (context manager style) configured from app config

    expects the following to be set in config: RSU_KEY, RSU_SECRET, RSU_API_REG_TOKEN, RSU_API_REG_SECRET

    :param kwargs: additional RunSignUp() arguments, e.g. debug=True
    '''
    return RunSignUp(
        key=current_app.config['RSU_KEY'],
        secret=current_app.config['RSU_SECRET'],
        api_reg_token=current_app.config['RSU_API_REG_TOKEN'],
        api_reg_secret=current_app.config['RSU_API_REG_SECRET'],
        **kwargs
    )
