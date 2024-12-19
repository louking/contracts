'''
helpers - commonly needed utilities
====================================================================================
'''

# standard

# pypi
from flask import g

# homegrown
from .dbmodel import LocalInterest
from loutilities.user.model import Interest

def localinterest():
    interest = Interest.query.filter_by(interest=g.interest).one()
    return LocalInterest.query.filter_by(interest_id=interest.id).one()
