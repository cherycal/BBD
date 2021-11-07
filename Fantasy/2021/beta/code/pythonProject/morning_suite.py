import sys
sys.path.append('./modules')
import time

exec(open('odds.py').read())
time.sleep(4)
exec(open('statcast_park_factors.py').read())
time.sleep(4)
exec(open('statcast_event_level.py').read())
time.sleep(4)
exec(open('team_splits.py').read())
time.sleep(4)
exec(open('fangraphs_splits.py').read())
