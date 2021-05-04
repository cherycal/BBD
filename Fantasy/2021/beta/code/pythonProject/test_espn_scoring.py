__author__ = 'chance'

from bs4 import BeautifulSoup
import time
import json
import os
import sys
import time
import urllib.request
import datetime
from datetime import date, time, timedelta, datetime
import pandas as pd

sys.path.append('./modules')
import sqldb
import fantasy

# My python class: sqldb.py

mode = "PROD"
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()
statid_dict = fantasy.get_statid_dict(verbose=False)

league = 6455
year = 2020


def one_day(scoring_period):
	addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/" + str(year) + \
	       "/segments/0/leagues/" + str(league) + "?" \
	                                              "view=mScoreboard&scoringPeriodId=" + str(scoring_period)
	print(addr)

	date8 = fantasy.get_date_from_scoring_id(year, scoring_period)

	with urllib.request.urlopen(addr) as url:
		data = json.loads(url.read().decode())
		scoring_items = data['settings']['scoringSettings']['scoringItems']
		stat_categories = []
		for scoring_item in scoring_items:
			stat_categories.append(scoring_item['statId'])
		for teams in data['schedule'][0]['teams']:
			team_id = teams['teamId']
			entries = teams['rosterForCurrentScoringPeriod']['entries']
			for entry in entries:
				lineup_slot = entry['lineupSlotId']
				player_id = entry['playerPoolEntry']['player']['id']
				player_name = entry['playerPoolEntry']['player']['fullName']
				points = None
				if 'appliedStatTotal' in entry['playerPoolEntry']:
					points = entry['playerPoolEntry']['appliedStatTotal']
				if len(entry['playerPoolEntry']['player']['stats']) > 0:
					player_stats = entry['playerPoolEntry']['player']['stats'][0]['stats']
					# print("______")
					lol = []
					cols = ['Name', 'playerid', 'Date', 'leagueId',
					        'teamId', 'lineupSlotId', 'points']
					vals = ['', 0, 0, 0, 0, 0, None]
					hasstats = 0
					for stat in player_stats:
						stat_int = int(stat)
						if stat_int in statid_dict:
							hasstats = 1
							vals[0] = player_name
							vals[1] = player_id
							vals[2] = date8
							vals[3] = league
							vals[4] = team_id
							vals[5] = fantasy.get_position(lineup_slot)
							vals[6] = points
							cols.append(str(statid_dict[stat_int]))
							vals.append(player_stats[stat])
						# print(player_name + " :teamid: " + str(team_id) + " :lineupslot: " +
						#       fantasy.get_position(lineup_slot) +
						#       " :stat: " + stat + " :id: " + str(player_id) +
						#       " :statname: " + str(statid_dict[stat_int]) +
						#       " :value: " + str(player_stats[stat]) + " :date: " + str(date8) )
						else:
							pass
					# print("Stat not found: " + str(stat) + " Value: " + str(player_stats[stat]))
					if hasstats:
						# print(cols)
						# print(vals)
						lol.append(vals)
						df = pd.DataFrame(lol, columns=cols)
						table_name = "ESPNDailyScoring"
						df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


for i in range(186, 188, 1):
	one_day(i)

bdb.close()
