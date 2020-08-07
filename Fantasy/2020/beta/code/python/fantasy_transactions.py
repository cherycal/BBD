import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools, fantasy
import pickle
import os.path
from os import path
import push
import random

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
date_time2 = now.strftime("%Y%m%d-%H%M%S")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

# for positionID in fantasy.position:
#     print(positionID)
#     print(fantasy.position[positionID])

# for ownerID in fantasy.ownerTeam:
#     print(ownerID)
#     print(fantasy.ownerTeam[ownerID])

# for LeagueID in fantasy.teamName:
#     print(LeagueID)
#     for teamID in fantasy.teamName[LeagueID]:
#         print(teamID)
#         print(fantasy.teamName[LeagueID][teamID])

# for MLBTeamID in fantasy.MLBTeamName:
#     print(MLBTeamID)
#     print(fantasy.MLBTeamName[MLBTeamID])
#fantasy.populate_team_owners('37863846')


teams = fantasy.active_leagues
while 1:
    fantasy.run_transactions(teams)
    num1 = random.randint(10, 100)
    now = datetime.now()  # current date and time
    date_time2 = now.strftime("%Y%m%d-%H%M%S")
    print(date_time2)
    time.sleep(num1)
