import json
import urllib.request
import sys
import time
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path

#url_name = "https://fantasy.espn.com/apis/v3/games/flb/seasons/2020/players?scoringPeriodId=0&view=players_wl"
#url_name = "https://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/162788?view=mPendingTransactions&view=mSettings&view=mStatus&view=mMatchupScore&view=mTeam&view=modular&view=mNav"
url_name = "download.json"

print(url_name)

bdb = sqldb.DB('Baseball.db')

with urllib.request.urlopen(url_name) as url:
    json_object = json.loads(url.read().decode())

    json_formatted = json.dumps(json_object, indent=2)

    print(json_formatted)
