# see https://stackoverflow.com/a/28154841/799921 solution #2
import sys
import os
from pathlib import Path
from time import time

if __name__ == '__main__' and not __package__:
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[2]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass

    # import contracts.scripts.unittest
    __package__ = 'contracts.scripts.unittest'
    
    from ... import create_app
    from ...dbmodel import db, SponsorRace
    from ...caching import update_raceregcache
    from ...settings import Development

    # create app and get configuration
    configfile = "contracts.cfg"
    configdir = os.path.abspath(__file__)
    # up three levels from file
    configdir = os.path.dirname(configdir)
    configdir = os.path.dirname(configdir)
    configdir = os.path.dirname(configdir)
    configpath = os.path.join(configdir, 'config', configfile)
    userconfigpath = os.path.join(configdir, 'config', 'users.cfg')
    # userconfigpath first so configpath can override
    configfiles = [userconfigpath, configpath]
    app = create_app(Development(configfiles), configfiles)

    with app.app_context():
        try:
            races = SponsorRace.query.filter_by(display=True).all()

            for race in races:
                # skip races for which we have no api
                if race.couponprovider != 'RunSignUp' or not race.couponproviderid: continue

                # app.logger.info(f'query RSU for all events in {race.race}...')
                # start = time()
                # events = update_raceregcache(race.couponproviderid, onlyrecentevents=False)
                # app.logger.info(f'{len(events)} events found for {race.race}')
                # db.session.commit()
                # end = time()
                # duration = end-start
                # app.logger.info(f'all events duration={duration} for {race.race}')
                
                app.logger.info(f'query RSU for recent events in {race.race}...')
                start = time()
                events = update_raceregcache(race.couponproviderid)
                app.logger.info(f'{len(events)} events found for {race.race}')
                db.session.commit()
                end = time()
                duration = end-start
                app.logger.info(f'recent events duration={duration} for {race.race}')

        except:
            db.session.rollback()
            raise
    