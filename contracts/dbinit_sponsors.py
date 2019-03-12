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
from dbmodel import SponsorRace, SponsorLevel, SponsorBenefit
from dbmodel import ModelItem, initdbmodels

sponsorraces = [
    {'race'           : 'Frederick Women\'s Distance Festival', 
     'raceshort'      : 'wdf', 
     'racedirector'   : 'Harriet Langlois', 
     'raceurl'        : 'https://www.frederickwdf.com/', 
     'sponsorurl'     : 'https://www.frederickwdf.com/sponsors', 
     'email'          : 'info@frederickwdf.com', 
     'couponprovider' : 'RunSignUp',
     'description'    : None,
    },
    {'race'           : 'Frederick Market Street Mile', 
     'raceshort'      : 'msm', 
     'racedirector'   : 'Lou King', 
     'raceurl'        : 'https://www.frederickmarketstreetmile.com/', 
     'sponsorurl'     : 'https://www.frederickmarketstreetmile.com/sponsors', 
     'email'          : 'info@frederickmarketstreetmile.com', 
     'couponprovider' : 'RunSignUp',
     'description'    : None,
    },
    {'race'           : 'Frederick Summer Solstice 8K', 
     'raceshort'      : 'ss8k', 
     'racedirector'   : 'Alex Young', 
     'raceurl'        : 'https://www.frederickss8k.com/', 
     'sponsorurl'     : 'https://www.frederickss8k.com', 
     'email'          : 'info@frederickss8k.com', 
     'couponprovider' : 'RunSignUp',
     'description'    : None,
    },
    {'race'           : 'Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge', 
     'raceshort'      : 'rrun', 
     'racedirector'   : 'Crista Horn', 
     'raceurl'        : 'https://www.rickstrailrun.com/', 
     'sponsorurl'     : 'https://www.rickstrailrun.com/sponsors', 
     'email'          : 'info@rickstrailrun.com', 
     'couponprovider' : None,
     'description'    : None,
    },
]

sponsorlevels = [
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Market Street Mile').one,
     'level'            : 'Premier',
     'minsponsorship'   : 2000,
     'maxallowed'       : 1,
     'couponcount'      : 5,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Market Street Mile').one,
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : 8,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Market Street Mile').one,
     'level'            : 'Silver',
     'minsponsorship'   : 250,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Market Street Mile').one,
     'level'            : 'Bronze',
     'minsponsorship'   : 100,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Women\'s Distance Festival').one,
     'level'            : 'Premier',
     'minsponsorship'   : 3500,
     'maxallowed'       : None,
     'maxallowed'       : 1,
     'couponcount'      : 10,
     'display'          : False,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Women\'s Distance Festival').one,
     'level'            : 'Platinum-Plus',
     'minsponsorship'   : 1500,
     'maxallowed'       : 3,
     'couponcount'      : 5,
     'display'          : False,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Women\'s Distance Festival').one,
     'level'            : 'Platinum',
     'minsponsorship'   : 1000,
     'maxallowed'       : None,
     'couponcount'      : 4,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Women\'s Distance Festival').one,
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : None,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Women\'s Distance Festival').one,
     'level'            : 'Silver',
     'minsponsorship'   : 250,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Summer Solstice 8K').one,
     'level'            : 'Premier',
     'minsponsorship'   : 2500,
     'maxallowed'       : 1,
     'couponcount'      : 5,
     'display'          : False,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Summer Solstice 8K').one,
     'level'            : 'Platinum-Plus: Feed 15 children',
     'minsponsorship'   : 1500,
     'maxallowed'       : 3,
     'couponcount'      : 4,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Summer Solstice 8K').one,
     'level'            : 'Platinum: Feed 10 children',
     'minsponsorship'   : 1000,
     'maxallowed'       : None,
     'couponcount'      : 3,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Summer Solstice 8K').one,
     'level'            : 'Gold: Feed 5 children',
     'minsponsorship'   : 500,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Frederick Summer Solstice 8K').one,
     'level'            : 'Silver: Feed 3 children',
     'minsponsorship'   : 300,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge').one,
     'level'            : 'Bronze',
     'minsponsorship'   : 150,
     'maxallowed'       : None,
     'couponcount'      : None,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge').one,
     'level'            : 'Silver',
     'minsponsorship'   : 300,
     'maxallowed'       : None,
     'couponcount'      : 1,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge').one,
     'level'            : 'Gold',
     'minsponsorship'   : 500,
     'maxallowed'       : None,
     'couponcount'      : 2,
     'display'          : True,
    },
    {
     'race'             : SponsorRace.query.filter_by(race='Rick O\'Donnell 5.22 Mile Trail Run and Ultra Challenge').one,
     'level'            : 'Platinum',
     'minsponsorship'   : 1000,
     'maxallowed'       : None,
     'couponcount'      : 3,
     'display'          : True,
    },]

sponsorbenefits = [
]

# initialize these tables
sponsormodelitems = [
    ModelItem(SponsorRace, sponsorraces, False, 'race'),
    ModelItem(SponsorLevel, sponsorlevels, False, ['race_id/race.id', 'level']),
    ModelItem(SponsorBenefit, sponsorbenefits, True),
]

#----------------------------------------------------------------------
def dbinit_sponsors():
#----------------------------------------------------------------------
    initdbmodels(sponsormodelitems)