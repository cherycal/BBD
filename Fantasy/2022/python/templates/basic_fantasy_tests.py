import sys
import time

sys.path.append('../modules')
import sqldb
import push
import tools
import os
import fantasy

plat = tools.get_platform()
print(plat)
push_instance = push.Push()
mode = "PROD"

fantasy = fantasy.Fantasy(mode, caller=os.path.basename(__file__))

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

APIKEY = os.environ.get('APIKEY')
APISECRETKEY = os.environ.get('APISECRETKEY')
ACCESSTOKEN = os.environ.get('ACCESSTOKEN')
ACCESSTOKENSECRET = os.environ.get('ACCESSTOKENSECRET')
API_KEY = os.environ.get('api_key')
REG_ID = os.environ.get('reg_id')

count = 0
while count < 2:
    push_instance.send_message(f"basic_fantasy_tests message","basic_fantasy_tests subject")
    time.sleep(4)
    count += 1

#fantasy.refresh_statcast_schedule()
# fantasy.tweet_add_drops()p
# fantasy.run_injury_updates()
