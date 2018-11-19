###########################################################################################
# utils - miscellaneous utilities
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/19/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
utils - miscellaneous utilities
=======================================================================
'''

#----------------------------------------------------------------------
def time24(time):
#----------------------------------------------------------------------
    # handle case of no time supplied
    if not time: return '00:00'

    # split out ampm (see events.py datetime format 'h:mm a')
    thetime, ampm = time.split(' ')

    # split time into fields h:m[:s]
    fields = [int(t) for t in thetime.split(':')]

    # hopefully this error was detected before time was put into database
    if len(fields) < 2 or len(fields) > 3:
        raise parameterError, 'invalid time field {} detected'.format(time)
    
    # use 24 hour clock
    if ampm.lower() == 'pm':
        fields[0] += 12
    
    # build and return string hh:mm[:ss]
    fieldstrs = []
    for field in fields:
        fieldstrs.append(str(field).zfill(2))
    return ':'.join(fieldstrs)

