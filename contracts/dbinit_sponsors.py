###########################################################################################
# dbinit_sponsors - contracts database initialization configuration - sponsor tables
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/18/18        Lou King        Create
#
#   Copyright 2018 Lou King
###########################################################################################
'''
dbinit_sponsors - contracts database initialization configuration - sponsor tables
======================================================================================

Initializion for sponsorraces, sponsorlevels, sponsorbenefits tables
'''
from dbmodel import db
from dbmodel import SponsorRace, SponsorLevel, SponsorBenefit, SponsorRaceDate, SponsorRaceVbl
from dbmodel import ModelItem, initdbmodels, getmodelitems, priorityUpdater

sponsorraces = [
    {'race'             : 'Frederick Women\'s Distance Festival', 
     'raceshort'        : 'WDF', 
     'racedirector'     : 'Harriet Langlois', 
     'rdphone'          : '301-606-7855',
     'rdemail'          : 'harriet.langlois@steeplechasers.org',
     'isRDCertified'    : True,
     'raceurl'          : 'https://www.frederickwdf.com/', 
     'sponsorurl'       : 'https://www.frederickwdf.com/sponsors', 
     'email'            : 'info@frederickwdf.com', 
     'couponprovider'   : 'RunSignUp',
     'couponproviderid' : '50830',
     'description'      : None,
     'display'          : True,
    },
    {'race'             : 'Frederick Market Street Mile', 
     'raceshort'        : 'MSM', 
     'racedirector'     : 'Lou King', 
     'rdphone'          : '240-397-9393',
     'rdemail'          : 'lou.king@steeplechasers.org',
     'isRDCertified'    : True,
     'raceurl'          : 'https://www.frederickmarketstreetmile.com/', 
     'sponsorurl'       : 'https://www.frederickmarketstreetmile.com/sponsors', 
     'email'            : 'info@frederickmarketstreetmile.com', 
     'couponprovider'   : 'RunSignUp',
     'couponproviderid' : '50864',
     'description'      : None,
     'display'          : True,
     },
    {'race'             : 'Frederick Summer Solstice 8K', 
     'raceshort'        : 'SS8K', 
     'racedirector'     : 'Alex Young', 
     'rdphone'          : None,
     'rdemail'          : 'alex.young@steeplechasers.org',
     'isRDCertified'    : False,
     'raceurl'          : 'https://www.frederickss8k.com/', 
     'sponsorurl'       : 'https://www.frederickss8k.com', 
     'email'            : 'info@frederickss8k.com', 
     'couponprovider'   : 'RunSignUp',
     'couponproviderid' : '55318',
     'description'      : None,
     'display'          : True,
     },
    {'race'             : 'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge', 
     'raceshort'        : 'RICKS', 
     'racedirector'     : 'Crista Horn', 
     'rdphone'          : None,
     'rdemail'          : 'crista.horn@steeplechasers.org',
     'isRDCertified'    : False,
     'raceurl'          : 'https://www.rickstrailrun.com/', 
     'sponsorurl'       : 'https://www.rickstrailrun.com/sponsors', 
     'email'            : 'info@rickstrailrun.com', 
     'couponprovider'   : None,
     'couponproviderid' : None,
     'description'      : None,
     'display'          : True,
     },
    {'race'             : 'Test Race', 
     'raceshort'        : 'TEST', 
     'racedirector'     : 'Lou King', 
     'rdphone'          : '240-397-9393',
     'rdemail'          : 'lou.king@steeplechasers.org',
     'isRDCertified'    : True,
     'raceurl'          : 'https://www.frederickmarketstreetmile.com/', 
     'sponsorurl'       : 'https://www.frederickmarketstreetmile.com/sponsors', 
     'email'            : 'lou.king@steeplechasers.org', 
     'couponprovider'   : 'RunSignUp',
     'couponproviderid' : '56880',
     'description'      : None,
     'display'          : False,
     },
]

sponsorlevels = [
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Test Race'}),
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : 1,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Test Race'}),
     'level'            : 'none',
     'minsponsorship'   : 0,
     'maxallowed'       : None,
     'couponcount'      : None,
     'display'          : False,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'level'            : 'Premier',
     'minsponsorship'   : 2000,
     'maxallowed'       : 1,
     'couponcount'      : 5,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : 8,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'level'            : 'Silver',
     'minsponsorship'   : 250,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'level'            : 'Bronze',
     'minsponsorship'   : 100,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'level'            : 'none',
     'minsponsorship'   : 0,
     'maxallowed'       : None,
     'couponcount'      : None,
     'display'          : False,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'Premier',
     'minsponsorship'   : 3500,
     'maxallowed'       : None,
     'maxallowed'       : 1,
     'couponcount'      : 10,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'Platinum-Plus',
     'minsponsorship'   : 1500,
     'maxallowed'       : 3,
     'couponcount'      : 5,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'Platinum',
     'minsponsorship'   : 1000,
     'maxallowed'       : None,
     'couponcount'      : 4,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : None,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'Silver',
     'minsponsorship'   : 250,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'none',
     'minsponsorship'   : 0,
     'maxallowed'       : None,
     'couponcount'      : None,
     'display'          : False,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Premier',
     'minsponsorship'   : 2500,
     'maxallowed'       : 1,
     'couponcount'      : 5,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Platinum-Plus',
     'minsponsorship'   : 1500,
     'maxallowed'       : 3,
     'couponcount'      : 4,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Platinum',
     'minsponsorship'   : 1000,
     'maxallowed'       : None,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Silver',
     'minsponsorship'   : 300,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Water Stop',
     'minsponsorship'   : 0,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : False,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'none',
     'minsponsorship'   : 0,
     'maxallowed'       : None,
     'couponcount'      : None,
     'display'          : False,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'level'            : 'Bronze',
     'minsponsorship'   : 150,
     'maxallowed'       : None,
     'couponcount'      : None,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'level'            : 'Silver',
     'minsponsorship'   : 300,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'level'            : 'Platinum',
     'minsponsorship'   : 1000,
     'maxallowed'       : None,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'level'            : 'none',
     'minsponsorship'   : 0,
     'maxallowed'       : None,
     'couponcount'      : None,
     'display'          : False,
    },
]

# sponsor benefits
sponsorbenefits = []
benefitvariables = []

# TEST sponsorship
benefitvariables += [
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Test Race'}),
        'variable'  : '_coupondate_',
        'value'     : '*TEST coupon deadline*',
    },
]

benefitpriority = priorityUpdater(10, 10)   # reset
sponsorbenefits += [
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Test Race'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Postcards, Posters (commit by April 1)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'TEST', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Test Race'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on home page of Race Website',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'TEST', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Test Race'}),
     'order'        : benefitpriority(),
     'benefit'      : '{{ _couponcount_ }} complimentary race entries - use coupon code <b>{{ couponcode }}</b> by {{ _coupondate_ }}',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'TEST', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Test Race'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Bib',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'TEST', 'level': 'Gold'}])
    },
]

# MSM sponsorship
benefitvariables += [
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
        'variable'  : '_coupondate_',
        'value'     : 'Sep 11',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
        'variable'  : '_shirtfrontdate_',
        'value'     : 'Aug 1',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
        'variable'  : '_shirtbackdate_',
        'value'     : 'Aug 15',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
        'variable'  : '_posterdate_',
        'value'     : 'Apr 1',
    },
]

benefitpriority = priorityUpdater(10, 10)   # reset
sponsorbenefits += [
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Postcards, Posters (commit by {{ _posterdate_ }})',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on home page of Race Website',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Bib',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Opportunity to speak at Awards Ceremony',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo incorporated into artwork on front of race Shirt (commit by {{ _shirtfrontdate_ }})',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}, {'race_short': 'MSM', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Registration Page',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}, {'race_short': 'MSM', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Email Promotion: Inclusion on mass emails (over 12,000 recipients)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}, {'race_short': 'MSM', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Race Day Announcements Recognition',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}, {'race_short': 'MSM', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on back of Race Shirt (commit by {{ _shirtbackdate_ }})',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}, {'race_short': 'MSM', 'level': 'Gold'}, {'race_short': 'MSM', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : '3\' x 6\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Shared Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Gold'}, {'race_short': 'MSM', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : '{{ _couponcount_ }} complimentary race entries - use coupon code <b>{{ couponcode }}</b> by {{ _coupondate_ }}',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}, {'race_short': 'MSM', 'level': 'Gold'}, {'race_short': 'MSM', 'level': 'Silver'}, {'race_short': 'MSM', 'level': 'Bronze'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Dedicated Thank You/Recognition on Facebook',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Premier'}, {'race_short': 'MSM', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Shared Thank You/Recognition on Facebook',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'MSM', 'level': 'Silver'}, {'race_short': 'MSM', 'level': 'Bronze'}])
    }
]

# WDF sponsorship
benefitpriority = priorityUpdater(10, 10)   # reset
benefitvariables += [
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
        'variable'  : '_coupondate_',
        'value'     : 'July 31',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
        'variable'  : '_shirtbackdate_',
        'value'     : 'June 20',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
        'variable'  : '_posterdate_',
        'value'     : 'Apr 1',
    },
]

sponsorbenefits += [
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : '5\' x 10\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : '3\' x 6\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Platinum-Plus'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : '2\' x 6\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Platinum'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : '2\' x 5\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Shared Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on home page of Race Website',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Postcards, Posters',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Opportunity to speak at Awards Ceremony',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Call-out in published press releases',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Bib',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Race Day Expo Booth Prime Location',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Race Day Water Stop with Branding',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Platinum-Plus'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Email Promotion: Inclusion on mass emails (over 12,000 recipients)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'},{'race_short':'WDF', 'level': 'Platinum'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo/Link on Race Registration Page',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'},{'race_short':'WDF', 'level': 'Platinum'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Sponsor-supplied materials included in race bags',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'},{'race_short':'WDF', 'level': 'Platinum'},{'race_short':'WDF', 'level': 'Gold'}])
    },
        {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on race shirt (commit by {{ _shirtfrontdate_ }})',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'},{'race_short':'WDF', 'level': 'Platinum'},{'race_short':'WDF', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Race Day Expo Space (10\'x10\')',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'},{'race_short':'WDF', 'level': 'Platinum'},{'race_short':'WDF', 'level': 'Gold'},{'race_short':'WDF', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Dedicated Thank you Facebook Page',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum'},{'race_short':'WDF', 'level': 'Platinum-Plus'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Shared Thank you on Facebook Page',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Gold'},{'race_short':'WDF', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on race website sponsor page',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'},{'race_short':'WDF', 'level': 'Platinum'},{'race_short':'WDF', 'level': 'Gold'},{'race_short':'WDF', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : '{{ _couponcount_ }} complimentary race entries - use coupon code <b>{{ couponcode }}</b> by {{ _coupondate_ }}',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'WDF', 'level': 'Premier'},{'race_short':'WDF', 'level': 'Platinum-Plus'},{'race_short':'WDF', 'level': 'Platinum'},{'race_short':'WDF', 'level': 'Gold'},{'race_short':'WDF', 'level': 'Silver'}])
    },
]

# SS8K sponsorship
benefitpriority = priorityUpdater(10, 10)   # reset
benefitvariables += [
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
        'variable'  : '_coupondate_',
        'value'     : 'June 10',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
        'variable'  : '_shirtbackdate_',
        'value'     : 'May 16',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
        'variable'  : '_posterdate_',
        'value'     : 'Apr 1',
    },
]

sponsorbenefits += [
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Feed 25 Children for One Year',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Feed 15 Children for One Year',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Platinum-Plus'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Feed 10 Children for One Year',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Platinum'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Feed 5 Children for One Year',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Feed 3 Children for One Year',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Name/Logo on race website banner, Race Flyer and Poster',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Bib',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Opportunity to Speak at Awards Ceremony',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Unique Venue Recognition (Contact us for Details)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Start/Finish Line Banner on Arch',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on Race Sign-up Page',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Logo on race website (sponsor section)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Email Promotion - Mass Mailing (12,000 recipients)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Race Day Expo Space (10\' x 10\' with table)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : '3\'x6\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : '2\'x6\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : '2\'x5\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Shared Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Silver'},{'race_short':'SS8K', 'level': 'Water Stop'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Name/Logo on race shirt (Must commit by {{ _shirtbackdate_ }})',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'},{'race_short':'SS8K', 'level': 'Silver'},{'race_short':'SS8K', 'level': 'Water Stop'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Race Day Recognition',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'},{'race_short':'SS8K', 'level': 'Silver'},{'race_short':'SS8K', 'level': 'Water Stop'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : '{{ _couponcount_ }} complimentary race entries - use coupon code <b>{{ couponcode }}</b> by {{ _coupondate_ }}',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'},{'race_short':'SS8K', 'level': 'Silver'},{'race_short':'SS8K', 'level': 'Water Stop'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Promotional Material on Shared Table',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'},{'race_short':'SS8K', 'level': 'Silver'},{'race_short':'SS8K', 'level': 'Water Stop'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Dedicated Facebook Thank You/Recognition',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Premier'},{'race_short':'SS8K', 'level': 'Platinum-Plus'},{'race_short':'SS8K', 'level': 'Platinum'},{'race_short':'SS8K', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Shared Facebook Thank You/Recognition',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'SS8K', 'level': 'Silver'},{'race_short':'SS8K', 'level': 'Water Stop'}])
    },
]

# RICK'S sponsorship
benefitpriority = priorityUpdater(10, 10)   # reset
benefitvariables += [
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
        'variable'  : '_coupondate_',
        'value'     : 'Sep 19',
    },
    {
        'race'      : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
        'variable'  : '_shirtbackdate_',
        'value'     : 'Aug 15',
    },
]

sponsorbenefits += [
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Name included on race venue signage',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Silver'},{'race_short':'RICKS', 'level': 'Bronze'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Dedicated large banner at race venue',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Platinum'},{'race_short':'RICKS', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Name/Logo on race website',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Platinum'},{'race_short':'RICKS', 'level': 'Gold'},{'race_short':'RICKS', 'level': 'Silver'},{'race_short':'RICKS', 'level': 'Bronze'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Acknowledgment on race facebook page',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Platinum'},{'race_short':'RICKS', 'level': 'Gold'},{'race_short':'RICKS', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Option to set up booth/tent at race venue',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Platinum'},{'race_short':'RICKS', 'level': 'Gold'},{'race_short':'RICKS', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Acknowledgment at FCPS Awards Ceremony',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Platinum'},{'race_short':'RICKS', 'level': 'Gold'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : '{{ _couponcount_ }} complimentary race entries - use coupon code <b>{{ couponcode }}</b>',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Platinum'},{'race_short':'RICKS', 'level': 'Gold'},{'race_short':'RICKS', 'level': 'Silver'}])
    },
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
     'order'        : benefitpriority(),
     'benefit'      : 'Recognized in email listing reaching thousands of runners',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short':'RICKS', 'level': 'Platinum'},{'race_short':'RICKS', 'level': 'Gold'},{'race_short':'RICKS', 'level': 'Silver'},{'race_short':'RICKS', 'level': 'Bronze'}])
    },
]

# initial sponsor race dates
sponsorracedates = [
    {
        'raceyear'      : 2019,
        'race'          : getmodelitems(SponsorRace,{'race':'Frederick Market Street Mile'}),
        'racedate'      : '2019-09-14',
        'beneficiary'   : 'Advocates for Homeless Families and Lincoln Elementary School Panther Running Club',
        'raceloc'       : 'the YMCA, 1000 N. Market St., Frederick',
    },
    {
        'raceyear'      : 2019,
        'race'          : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
        'racedate'      : '2019-08-03',
        'beneficiary'   : 'Women\'s Giving Circle of Frederick County',
        'raceloc'       : 'Frederick Community College, 7932 Opossumtown Pike, Frederick',
    },
    {
        'raceyear'      : 2019,
        'race'          : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
        'racedate'      : '2019-06-15',
        'beneficiary'   : 'Frederick chapter of Blessings in a Backpack',
        'raceloc'       : 'the Walkersville Fire Hall, 79 West Frederick St, Walkersville',
    },
    {
        'raceyear'      : 2019,
        'race'          : getmodelitems(SponsorRace,{'race':'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge'}),
        'racedate'      : '2019-09-22',
        'beneficiary'   : 'Frederick Steeplechasers Memorial Scholarship',
        'raceloc'       : 'Greenbrier State Park, Boonsboro',
    },
]

# initialize these tables
sponsormodelitems = [
    ModelItem(SponsorRace, sponsorraces, False, 'race'),
    ModelItem(SponsorLevel, sponsorlevels, False, ['race_id/race.id', 'level']),
    ModelItem(SponsorRaceVbl, benefitvariables, False, ['race_id/race.id', 'variable']),
    ModelItem(SponsorRaceDate, sponsorracedates, False, ['race_id/race.id', 'raceyear']),
    ModelItem(SponsorBenefit, sponsorbenefits, True),
]

#----------------------------------------------------------------------
def dbinit_sponsors():
#----------------------------------------------------------------------
    initdbmodels(sponsormodelitems)