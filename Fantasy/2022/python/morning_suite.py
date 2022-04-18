import sys
sys.path.append('./modules')
import time

time.sleep(1)
exec(open('odds.py').read())
time.sleep(1)
#exec(open('statcast_park_factors.py').read())
time.sleep(1)
exec(open('statcast_event_level.py').read())
time.sleep(1)
#exec(open('team_splits.py').read())
time.sleep(1)
exec(open('fangraphs_splits.py').read())
time.sleep(1)
exec(open('statcast_daily_level.py').read())
time.sleep(4)
exec(open('espn_daily_scoring_to_db.py').read())
time.sleep(4)
exec(open('savant_boxscores.py').read())
time.sleep(4)
exec(open('add_to_id_map.py.py').read())

