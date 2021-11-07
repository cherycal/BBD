import sys
sys.path.append('./modules')
import time

exec(open('odds.py').read())
#time.sleep(4)
exec(open('espn_daily_scoring_to_db.py').read())
time.sleep(4)
exec(open('savant_boxscores.py').read())

