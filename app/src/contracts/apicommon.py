'''
apicommon - helper functions for api building
==================================================
'''

# standard

# pypi
from flask import jsonify

def success_response(**respargs):
    '''
    build success response for API
    
    :param respargs: arguments for response
    :rtype: json response
    '''

    return jsonify(success=True,**respargs)

def failure_response(**respargs):
    '''
    build failure response for API
    
    :param respargs: arguments for response
    :rtype: json response
    '''

    return jsonify(success=False,**respargs)

