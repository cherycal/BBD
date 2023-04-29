import sys

sys.path.append('./modules')
import time
import push

inst = push.Push()

# scripts = ['espn_season_stats.py',
#            'espn_daily_scoring_to_db.py', 'espn_standings.py', 'odds.py', 'statcast_event_level.py',
#            'statcast_daily_level.py', 'savant_boxscores.py', 'team_splits.py', 'tables_to_files.py']

scripts = ['espn_daily_scoring_to_db.py', 'espn_standings.py', 'odds.py', 'statcast_event_level.py',
           'statcast_season_level.py',
           'espn_season_stats.py', 'savant_boxscores.py', 'team_splits.py']


for script in scripts:
    try:
        exec(open(script).read())
        print(f'Script {script} succeeded')
    except Exception as ex:
        print(f'Script {script} failed with error {ex}')
        inst.push("Morning suite process error:", f'Error: {ex}\nFunction: {script}')
    time.sleep(1)

    # exec(open('espn_daily_scoring_to_db.py').read())
    # time.sleep(4)
    # exec(open('espn_standings.py').read())
    # time.sleep(1)
    # exec(open('odds.py').read())
    # time.sleep(1)
    # #exec(open('statcast_park_factors.py').read())
    # time.sleep(1)
    # exec(open('statcast_event_level.py').read())
    # time.sleep(1)
    # exec(open('statcast_daily_level.py').read())
    # time.sleep(4)
    # exec(open('savant_boxscores.py').read())
    # time.sleep(1)
    # exec(open('team_splits.py').read())
    # time.sleep(1)
    # exec(open('espn_season_stats.py').read())

######### DECOMMISSIONED ######################
# time.sleep(4)
# exec(open('fangraphs_splits.py').read())
# time.sleep(4)
# exec(open('add_to_id_map.py').read())
