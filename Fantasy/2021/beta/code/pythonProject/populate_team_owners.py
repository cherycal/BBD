import sys
import time
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import json
import sys
import time
import urllib.request
from datetime import datetime, timedelta
import fantasy
import inspect
import random

mode = "PROD"

fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()

def populate_team_owners(leagueID, year):
	url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/" + str(year) + \
	           "/segments/0/leagues/" + \
	           str(leagueID)
	print("populate_team_owners: " + url_name)
	with urllib.request.urlopen(url_name) as url:
		json_object = json.loads(url.read().decode())

		# json_formatted = json.dumps(json_object, indent=2)
		for team in json_object['teams']:
			print("Team:")
			print(team)
			for owner in team['owners']:
				insert_list = [owner, str(leagueID), str(team['id']),
				               str(team['location']) + " " + team['nickname']]
				bdb.insert_list("ESPNTeamOwners", insert_list)


populate_team_owners(3154,2021)
