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
from dbmodel import SponsorRace, SponsorLevel, SponsorBenefit, SponsorRaceVbl
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
    },
    {'race'             : 'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge', 
     'raceshort'        : 'RICK\'S', 
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
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'Premier',
     'minsponsorship'   : 3500,
     'maxallowed'       : None,
     'maxallowed'       : 1,
     'couponcount'      : 10,
     'display'          : False,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'level'            : 'Platinum-Plus',
     'minsponsorship'   : 1500,
     'maxallowed'       : 3,
     'couponcount'      : 5,
     'display'          : False,
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
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Premier',
     'minsponsorship'   : 2500,
     'maxallowed'       : 1,
     'couponcount'      : 5,
     'display'          : False,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Platinum-Plus: Feed 15 children',
     'minsponsorship'   : 1500,
     'maxallowed'       : 3,
     'couponcount'      : 4,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Platinum: Feed 10 children',
     'minsponsorship'   : 1000,
     'maxallowed'       : None,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Gold: Feed 5 children',
     'minsponsorship'   : 500,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : getmodelitems(SponsorRace,{'race':'Frederick Summer Solstice 8K'}),
     'level'            : 'Silver: Feed 3 children',
     'minsponsorship'   : 300,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : True,
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
    },]

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
     'benefit'      : 'Three (3) complimentary race entries - use coupon code <b>{{ couponcode }}</b> by {{ _coupondate_ }}',
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
     'benefit'      : 'Included on Race Promotion mass email',
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
     'benefit'      : '{{ _couponcount_ }} complimentary race entries  - use coupon code <b>{{ couponcode }}</b> by {{ _coupondate_ }}',
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

benefitpriority = priorityUpdater(10, 10)   # reset
# WDF sponsorship
sponsorbenefits += [
    {
     'race'         : getmodelitems(SponsorRace,{'race':'Frederick Women\'s Distance Festival'}),
     'order'        : benefitpriority(),
     'benefit'      : '5\' x 10\' Race Day Banner (supplied by us)',
     'description'  : None,
     'levels'       : getmodelitems(SponsorLevel,[{'race_short': 'WDF', 'level': 'Premier'}])
    },
]

# initialize these tables
sponsormodelitems = [
    ModelItem(SponsorRace, sponsorraces, False, 'race'),
    ModelItem(SponsorLevel, sponsorlevels, False, ['race_id/race.id', 'level']),
    ModelItem(SponsorRaceVbl, benefitvariables, False, ['race_id/race.id', 'variable']),
    ModelItem(SponsorBenefit, sponsorbenefits, True),
]

#----------------------------------------------------------------------
def dbinit_sponsors():
#----------------------------------------------------------------------
    initdbmodels(sponsormodelitems)