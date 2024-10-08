import sys

sys.path.append('./modules')
import json
import urllib.request
import fantasy

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
				               str(team['location']) + " " + str(team['nickname']),
				               str(team['location']) + " " + str(team['nickname']),'0']
				bdb.insert_list("ESPNTeamOwners", insert_list)



populate_team_owners(1190388698, 2023)
populate_team_owners(941700542, 2023)


