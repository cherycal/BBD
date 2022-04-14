__author__ = 'chance'

import json
import sys
import urllib.request
from datetime import date, timedelta

import pandas as pd

sys.path.append('./modules')
import fantasy
import os

# My python class: sqldb.py

# NB: Use create_daily_scoring_table.py to create the ESPNDailyScoring table

mode = "PROD"
fantasy = fantasy.Fantasy(mode, caller=os.path.basename(__file__))
bdb = fantasy.get_db()
statid_dict = fantasy.get_statid_dict(verbose=False)

year = 2022


def one_day(scoring_period, league):
	addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/" + str(year) + \
	       "/segments/0/leagues/" + str(league) + "?" \
	                                              "view=mScoreboard&scoringPeriodId=" + str(scoring_period)
	print(addr)

	date8 = fantasy.get_date_from_scoring_id(year, scoring_period)

	with urllib.request.urlopen(addr) as url:
		data = json.loads(url.read().decode())
		scoring_items = data['settings']['scoringSettings']['scoringItems']
		stat_categories = []
		lol = list()
		for scoring_item in scoring_items:
			stat_categories.append(scoring_item['statId'])
		for teams in data['schedule'][0]['teams']:
			team_id = teams['teamId']
			entries = teams['rosterForCurrentScoringPeriod']['entries']
			table_name = "ESPNDailyScoring"
			delcmd = "delete from " + table_name + " where Date = " + \
			         str(date8) + " and LeagueID = " + str(league) + \
			         " and teamID = " + str(team_id)
			#print(delcmd)

			bdb.delete(delcmd)

			for entry in entries:
				entryhasstats = 0
				lineup_slot = entry['lineupSlotId']
				player_id = entry['playerPoolEntry']['player']['id']
				player_name = entry['playerPoolEntry']['player']['fullName']
				points = None
				if 'appliedStatTotal' in entry['playerPoolEntry']:
					points = entry['playerPoolEntry']['appliedStatTotal']
				if len(entry['playerPoolEntry']['player']['stats']) > 0:
					for game in entry['playerPoolEntry']['player']['stats']:
						lol.clear()
						player_stats = game['stats']
						cols = ['Name', 'playerid', 'Date', 'leagueId',
						        'teamId', 'lineupSlotId', 'points']
						vals = ['', 0, 0, 0, 0, 0, None]
						vals[0] = player_name
						vals[1] = player_id
						vals[2] = date8
						vals[3] = league
						vals[4] = team_id
						vals[5] = fantasy.get_position(lineup_slot)
						vals[6] = 0
						for stat in player_stats:
							stat_int = int(stat)
							if stat_int in statid_dict:
								entryhasstats = 1
								vals[0] = player_name
								vals[1] = player_id
								vals[2] = date8
								vals[3] = league
								vals[4] = team_id
								vals[5] = fantasy.get_position(lineup_slot)
								vals[6] = points
								cols.append(str(statid_dict[stat_int]))
								vals.append(player_stats[stat])

						# print("Stat not found: " + str(stat) +
						# " Value: " + str(player_stats[stat]))
						if entryhasstats or True:
							lol.append(vals)
							#print(vals)
							df = pd.DataFrame(lol, columns=cols)
							table_name = "ESPNDailyScoring"
							tries = 0
							max_tries = 4
							incomplete = True
							while incomplete and tries < max_tries:
								try:
									df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
									incomplete = False
									#print("DB insert succeeded on try {}".format(tries + 1))
								except Exception as ex:
									print(str(ex))
									tries += 1
							if tries >= max_tries:
								print("DB insert failed")
								exit(-1)

def main():
	leagues = [6455, 37863846,1095816069]
	#leagues = [162788]
	season_start = date(2022, 4, 7)
	today = date.today()
	#previous = today - timedelta(days=2)
	previous = today - timedelta(days=1)

	#print(yesterday.strftime("%Y%m%d"))

	today_scoring_pd = (today - season_start).days
	previous_scoring_pd = (previous - season_start).days

	#five_days_ago = today - timedelta(days=5)
	#five_ago_scoring_pd = (five_days_ago - season_start).days

	start_scoring_pd = previous_scoring_pd
	end_scoring_pd = today_scoring_pd + 2


	## Override for ad hoc runs
	override = False
	if override:

		start_date = date(2021, 4, 15)
		end_date = date(2021, 5, 16)

		start_scoring_pd = (start_date - season_start).days
		end_scoring_pd = (end_date - season_start).days



	for lg in leagues:
		for i in range(start_scoring_pd, end_scoring_pd, 1):
			one_day(i, lg)

	bdb.close()


if __name__ == "__main__":
	main()
