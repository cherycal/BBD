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

url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/162788"

print(url_name)

bdb = sqldb.DB('Baseball.db')

with urllib.request.urlopen(url_name) as url:
    json_object = json.loads(url.read().decode())

    json_formatted = json.dumps(json_object, indent=2)
    #print(json_formatted)

    for i in json_object['teams']:
        for owner in i['owners']:
            print(i)
            name = i['location'] + ' ' + i['nickname']
            bdb.insert("INSERT INTO ESPNTeamOwners(OwnerId, LeagueID, TeamID, TeamName) VALUES (\"" +
                       str(owner) + "\",162788," + str(i['id']) + ",\"" + name + "\")")
