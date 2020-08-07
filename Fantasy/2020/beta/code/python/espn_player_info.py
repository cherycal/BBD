import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

espn_player_info = fantasy.set_espn_player_json()

for player in espn_player_info['players']:
    player_list = list()
    player_list.append(player['id'])
    if 'injuryStatus' in player['player']:
        player_list.append(player['player']['injuryStatus'])
    else:
        player_list.append("NA")
    player_list.append(player['status'])
    player_list.append(player['player']['fullName'])
    # noinspection SpellCheckingInspection
    if 'laterality' in player['player']:
        player_list.append(player['player']['laterality'])
    else:
        player_list.append("NA")
    if 'stance' in player['player']:
        player_list.append(player['player']['stance'])
    else:
        player_list.append("NA")
    if 'nextStartExternalId' in player['player']:
        player_list.append(player['player']['nextStartExternalId'])
    else:
        player_list.append("NA")
    if 'proTeamId' in player['player']:
        player_list.append(player['player']['proTeamId'])
    else:
        player_list.append("NA")
    if 'ownership' in player['player']:
        for i in player['player']['ownership']:
            player_list.append(round(player['player']['ownership'][i], 2))
    else:
        player_list.extend(["NA","NA","NA","NA","NA","NA","NA"])

    print_str = fantasy.string_from_list(player_list, delimiter=',')

    print(print_str)
