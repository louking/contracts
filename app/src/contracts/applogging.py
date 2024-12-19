#!/usr/bin/python
###########################################################################################
# applogging - define logging for the application
#
#   Date        Author          Reason
#   ----        ------          ------
#   07/06/18    Lou King        Create (from https://github.com/louking/rrwebapp/blob/master/rrwebapp/applogging.py)
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
applogging - define logging for the application
================================================
'''
# standard
from datetime import datetime

# pypi
from loutilities.timeu import asctime

# homegrown

# pick up common setlogging function (backwards compatibility)
from loutilities.user.applogging import setlogging


def timenow():
    """useful for logpoints"""
    return asctime('%H:%M:%S.%f').dt2asc(datetime.now())
