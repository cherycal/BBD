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

url_name = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"

print(url_name)

bdb = sqldb.DB('Baseball.db')

with urllib.request.urlopen(url_name) as url:
    json_object = json.loads(url.read().decode())

    json_formatted = json.dumps(json_object, indent=2)

    #print(json_formatted)

    for team in json_object['sports'][0]['leagues'][0]['teams']:
        print(team)
        #print(team['team']['id'] + ', ' + team['team']['abbreviation'])
        #bdb.insert("insert into ESPNTeams (TeamID, Team) VALUES (" + str(team['team']['id']) + ",\"" + str(team['team']['abbreviation']) + "\")")
