import json
import sys
import urllib.request

sys.path.append('./modules')
import sqldb
import time
import csv
from os import path
import random
import push
import pandas as pd
import fantasy
import dataframe_image as dfi
from datetime import datetime

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")

override_date = ""

if override_date != "":
	out_date = override_date

integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

watch_ids = list()
q = "select distinct MLBID from ( select  round(MLBID,0) as MLBID, Name," \
    "R.Team, AuctionValueAverage from ESPNPlayerDataCurrent E," \
    " IDMap I, ESPNRosters R where E.espnid = R.ESPNID and " \
    " E.espnid = I.ESPNID and AuctionValueAverage > 2 union " \
    "select  round(MLBID,0) as MLBID, Name, R.Team, AuctionValueAverage from " \
    "ESPNPlayerDataCurrent E, IDMap I, ESPNRosters R where " \
    "E.espnid = R.ESPNID and  E.espnid = I.ESPNID and " \
    "R.Team in ('When Franimals Attack' ,'SpringRakers' ))"

c = bdb.select(q)

for t in c:
	watch_ids.append(str(int(t[0])))

gamepks = list()

c = bdb.select("select game from StatcastGameData where date = " + str(out_date))
for t in c:
	gamepks.append(str(t[0]))

reported_event_count = dict()
event_count = dict()
has_statcast = dict()


def process_mlb(data, gamepk):
	global watch_ids
	global reported_event_count
	global event_count
	plays = data['liveData']['plays']['allPlays']
	print("Game: " + str(gamepk))
	# print(watch_ids)
	print("MLB data: events " + str(len(plays)))
	print("Previously reported events: " +
	      str(reported_event_count[gamepk]))
	for play in plays:
		event_count[gamepk] += 1
		if event_count[gamepk] > reported_event_count[gamepk]:
			batter_id = str(play['matchup']['batter']['id'])
			batter_name = str(play['matchup']['batter']['fullName'])
			pitcher_id = str(play['matchup']['pitcher']['id'])
			pitcher_name = str(play['matchup']['pitcher']['fullName'])
			print(batter_name)
			print(pitcher_name)
			if batter_id in watch_ids or pitcher_id in watch_ids:
				print(play)
				print("Batter: " + batter_id)
				print("Pitcher: " + pitcher_id)
				if play['result'].get('description'):
					print("-----------------------------------------------")
					print("event: " + str(event_count[gamepk]))
					msg = play['result']['description']
					msg += "\nPitcher: " + pitcher_name
					print("-----------------------------------------------")
					print(msg)
					print("-----------------------------------------------")
					title = msg[0:40]
					print("Pushing: " + msg)
					inst.push(title, msg)
					inst.tweet(msg)
					reported_event_count[gamepk] += 1
				else:
					print("Play has no description")
			else:
				print("-----------------------------------------------")
				print("Skipped play, players not on watch list: " +
				      str(event_count[gamepk]))
				print(play)
				print("-----------------------------------------------")
				reported_event_count[gamepk] += 1


def process_statcast(data, gamepk):
	global watch_ids
	global reported_event_count
	global event_count
	global out_date
	# msg2 = ""
	away_team = data['boxscore']['teams']['away']
	home_team = data['boxscore']['teams']['home']
	print("Game: " + str(gamepk))
	# print(watch_ids)
	for team in [home_team, away_team]:
		batlol = list()
		pitchlol = list()
		batters = team['batters']
		pitchers = team['pitchers']
		column_names = ['name', 'team', 'date', 'points', 'totalBases', 'runs', 'rbi', 'stolenBases',
		                'baseOnBalls', 'strikeOuts', 'doubles', 'triples', 'homeRuns',
		                'hits', 'atBats', 'caughtStealing', 'hitByPitch',
		                'groundIntoDoublePlay', 'mlbid']
		batcats = ['points', 'totalBases', 'runs', 'rbi', 'stolenBases',
		           'baseOnBalls', 'strikeOuts', 'doubles', 'triples', 'homeRuns',
		           'hits', 'atBats', 'caughtStealing', 'hitByPitch',
		           'groundIntoDoublePlay', 'mlbid', 'name', 'team', 'date']
		index = list()
		teamname = team['team']['name'].split(" ")[-1]

		for batter in batters:
			statlist = list()
			bid = "ID" + str(batter)
			bname = team['players'][bid]['person']['fullName']
			game_stats = team['players'][bid]['stats']['batting']
			for cat in batcats:
				if game_stats.get(cat):
					statlist.append(game_stats[cat])
				else:
					statlist.append(0)
			points = sum(statlist[1:6]) - statlist[6]
			statlist[-1] = out_date
			statlist[-2] = teamname
			statlist[-3] = bname
			statlist[-4] = bid[2:]
			statlist[0] = points
			batlol.append(statlist)
			index.append("")
			print(bid)
			print(bname)
			print(batcats)
			print(statlist)
			print("")

		df = pd.DataFrame(batlol, columns=batcats, index=index)
		print(df.columns)
		df = df.sort_values(by=['points'], ascending=[False])
		df = df[column_names]
		# df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
		img = "mytable.png"
		dfi.export(df, img)
		# inst.tweet_media(img, "Batting stats: " + teamname)

		table_name = "StatcastBoxscores"
		del_cmd = "delete from StatcastBoxscores where date = " + \
		          out_date + " and team = '" + teamname + "'"

		not_passed = True
		while not_passed:
			try:
				bdb.delete(del_cmd)
				not_passed = False
			except Exception as ex:
				print("DB Error")
				inst.push("DATABASE ERROR at " + str(date_time),
				          del_cmd + ": " + str(ex))
				time.sleep(15)

		df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

		column_names = ['name', 'team', 'date', 'points', 'qs', 'outs', 'strikeOuts', 'wins', 'saves', 'holds',
		                'earnedRuns', 'baseOnBalls', 'losses', 'hits', 'mlbid']

		pitchcats = ['points', 'qs', 'outs', 'strikeOuts', 'wins', 'saves', 'holds',
		             'earnedRuns', 'baseOnBalls', 'losses', 'hits', 'mlbid',
		             'name', 'team', 'date']

		index.clear()
		for pitcher in pitchers:
			pid = "ID" + str(pitcher)
			statlist = list()
			pname = team['players'][pid]['person']['fullName']
			game_stats = team['players'][pid]['stats']['pitching']
			print(pid)
			print(pname)
			print(game_stats)
			print("")
			qs = 0
			for cat in pitchcats:
				if game_stats.get(cat):
					statlist.append(game_stats[cat])
				else:
					statlist.append(0)
			if game_stats['outs'] >= 18 and game_stats['earnedRuns'] <= 3:
				qs = 1
			points = 2 * qs + game_stats['outs'] + game_stats['strikeOuts'] + \
			         game_stats['wins'] + \
			         5 * game_stats['saves'] + 3 * game_stats['holds'] - \
			         2 * game_stats['earnedRuns'] - \
			         game_stats['baseOnBalls'] - game_stats['losses'] - \
			         game_stats['hits']
			statlist[-1] = out_date
			statlist[-2] = teamname
			statlist[-3] = pname
			statlist[-4] = pid[2:]
			statlist[0] = points
			statlist[1] = qs
			pitchlol.append(statlist)
			print(pname)
			print(pitchcats)
			print(statlist)
			index.append("")

		df = pd.DataFrame(pitchlol, columns=pitchcats, index=index)
		print(df.columns)
		df = df.sort_values(by=['points'], ascending=[False])
		df = df[column_names]
		# df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
		img = "mytable.png"
		dfi.export(df, img)
		# inst.tweet_media(img, "Pitching stats: " + teamname)

		table_name = "StatcastBoxscoresPitching"
		del_cmd = "delete from " + table_name + " where date = " + \
		          out_date + " and team = '" + teamname + "'"
		bdb.delete(del_cmd)
		df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


def main():
	global has_statcast
	global reported_event_count
	global out_date

	# Tells program how many events have been reported for each game
	# So that events aren't reported more than once
	if path.exists("event_count.csv"):
		with open('event_count.csv', mode='r') as inp:
			reader = csv.reader(inp)
			reported_event_count = {str(rows[0]): int(rows[1]) for rows in reader}

	# Sets counts to zero if event counts are not found in event_count.csv file
	for gamepk in gamepks:
		if not event_count.get(gamepk):
			event_count[str(gamepk)] = 0
		if not reported_event_count.get(gamepk):
			reported_event_count[str(gamepk)] = 0
	# print(gamepk)
	# print(reported_event_count[gamepk])

	# for i in reported_event_count:
	#     print(i)
	#     print(reported_event_count[i])

	while 1:
		ts = datetime.now()  # current date and time
		formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
		for gamepk in gamepks:

			url_name = "https://baseballsavant.mlb.com/gf?game_pk=" + gamepk

			print(url_name)

			with urllib.request.urlopen(url_name) as url:
				event_count[gamepk] = 0
				data = json.loads(url.read().decode())

				if data.get('exit_velocity'):
					print("Reporting statcast data")
					process_statcast(data, gamepk)
				else:
					print("Statcast data unavailable, checking for MLB Data")
					url_name = "http://statsapi.mlb.com/api/v1.1/game/" + gamepk + "/feed/live"
					print(url_name)
					with urllib.request.urlopen(url_name) as url2:
						event_count[gamepk] = 0
						data = json.loads(url2.read().decode())
						if data.get('liveData'):
							print("Skipping MLB data")
						# process_mlb(data, gamepk)
						else:
							print("MLB data unavailable")

			# Record how many events have been reported to event_count.csv file
			with open('event_count.csv', 'w') as f:
				for key in reported_event_count.keys():
					f.write("%s,%s\n" % (key, reported_event_count[key]))
			f.close()

			# Records to the has_statcast.csv file from has_statcast dict
			with open('has_statcast.csv', 'w') as f:
				for key in has_statcast.keys():
					f.write("%s,%s\n" % (key, 1 * has_statcast[key]))
			f.close()

			print("Sleep at " + formatted_date_time)
			num1 = random.randint(4, 8)
			print("Sleep for " + str(num1) + " seconds")
			time.sleep(num1)
		exit(0)


if __name__ == "__main__":
	main()
