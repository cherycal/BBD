__author__ = 'chance'

import os
import os.path
import sys

import numpy as np
import pandas as pd

sys.path.append('./modules')
import requests

import time
import push
import tools
from datetime import timedelta, date
from pathlib import Path

inst = push.Push()

import sqldb

bdb = sqldb.DB('Baseball.db')

plat = tools.get_platform()
# print(plat)
cur_dir = Path.cwd()
data_dir = cur_dir / 'data'
data_dir.mkdir(mode=0o755, exist_ok=True)


def daterange(date1, date2):
	for n in range(int((date2 - date1).days) + 1):
		yield date1 + timedelta(n)


# https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=single%7Cdouble%7Ctriple
# %7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play
# %7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double
# %5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce
# %5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt
# %7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly
# %5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfGT=R%7C&hfPR=&hfZ=&stadium=
# &hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2019%7C&hfSit=&player_type=batter&hfOuts=
# &opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2019-07-17
# &game_date_lt=2019-07-17&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=
# &hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-event
# &sort_col=xwoba&player_event_sort=api_p_release_speed&sort_order=desc&min_pas=0&chk_event_launch_speed=on


# Pitch speed and spin rate
# &chk_event_release_spin_rate=on&chk_event_release_speed=on#results
# https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2020%7C&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2020-07-23&game_date_lt=2020-07-23&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-event&sort_col=xwoba&player_event_sort=api_p_release_speed&sort_order=desc&min_pas=0&chk_event_launch_speed=on&chk_event_launch_angle=on&chk_event_release_spin_rate=on&chk_event_release_speed=on&chk_event_hit_distance_sc=on&chk_event_estimated_ba_using_speedangle=on&chk_event_estimated_slg_using_speedangle=on&chk_event_estimated_woba_using_speedangle=on&type=details&
# https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2020%7C&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2020-07-23&game_date_lt=2020-07-23&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-event&sort_col=xwoba&player_event_sort=api_p_release_speed&sort_order=desc&min_pas=0&chk_event_launch_speed=on&chk_event_launch_angle=on&chk_event_release_spin_rate=on&chk_event_release_speed=on&chk_event_hit_distance_sc=on&chk_event_estimated_ba_using_speedangle=on&chk_event_estimated_slg_using_speedangle=on&chk_event_estimated_woba_using_speedangle=on#results

def single_day(**kwargs):
	return_value = 0
	year = kwargs['year']
	player_type = kwargs['player_type']
	override = kwargs['override']
	dt = str(kwargs['date'])
	dirname = kwargs['dir']
	tablename = 'Statcast' + dirname + 'Events'
	dt8 = str.replace(dt, "-", "")
	print("Date8: " + dt8)

	url_csv_text = "/csv?all=true&"

	url_base = "https://baseballsavant.mlb.com/statcast_search"

	url_basic_search_text = "?"

	if int(dt8) >= 20220407 or int(dt8) < 20220101:
		gt = "R"
	else:
		gt = "S"


	url_body = "hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%" \
	           "7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%" \
	           "7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7C" \
	           "fielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7C" \
	           "force%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7C" \
	           "sac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7C" \
	           "sac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%" \
	           "7Ctriple%5C.%5C.play%7C&hfGT=" + gt + "%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=" \
	           "&hfC=&hfSea=" + str(year) + "%7C&hfSit=&player_type=" \
	           + player_type + "&hfOuts=&opponent=&" \
	                           "pitcher_throws=&batter_stands=&hfSA=&game_date_gt=" + dt + \
	           "&game_date_lt=" + dt + \
	           "&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&" \
	           "min_results=0&group_by=name-event&sort_col=xwoba&player_event_sort=lineup_cd&" \
	           "sort_order=desc&min_pas=0"

	url_checks = "&chk_event_estimated_slg_using_speedangle=on"
	url_details = "&type=details&"
	url_footer = "#results"

	url_details_text = url_base + url_csv_text + url_body + url_checks + url_details
	url_text = url_base + url_basic_search_text + url_body + url_checks + url_footer

	print(url_details_text)
	print(url_text)

	print("sleeping ....")
	time.sleep(.5)

	r = requests.get(url_details_text, allow_redirects=True)
	filename = dirname + "_events_daily.csv"
	csvfile = data_dir / filename
	print(csvfile)
	open(csvfile, 'wb').write(r.content)
	df = pd.read_csv(csvfile, encoding='unicode_escape')

	df.rename(columns={'estimated_ba_using_speedangle': 'xBA', "estimated_woba_using_speedangle": "xwOBA"},
	          inplace=True)
	df['adj_xBA'] = 0.00
	df['adj_xwOBA'] = 0.00
	df['adj_xSLG'] = 0.00

	##################################################################################################
	##################################################################################################

	# page = requests.get(url_text)
	# soup = BeautifulSoup(page.content, 'html.parser')

	filename = dirname + "_events_daily.csv"
	csvfile2 = data_dir / filename
	# csvfile2 = "C:\\Users\\chery\\Documents\\BBD\\Statcast\\" + dirname + "\\" + "events_daily2.csv"

	try:
		df2 = pd.read_html(url_text)[0]
		df2.to_csv(csvfile2, index=False)
	except Exception as ex:
		print(str(ex))
		return 0

	if os.path.getsize(csvfile2) > 0:
		df2 = pd.read_csv(csvfile2, encoding='unicode_escape')

		df2.rename(columns={df2.columns[2]: "playerid"}, inplace=True)
		df2.rename(columns={df2.columns[1]: "Name"}, inplace=True)
		df2.rename(columns={df2.columns[4]: "gamedate"}, inplace=True)
		del df2['Unnamed: 7']

		print(df2.columns)

		df_combined = pd.concat([df, df2], axis=1)
		df_combined['player_name'] = df_combined['player_name'].str.encode("latin-1").str.decode("utf-8")
		df_combined['Name'] = df_combined['player_name']
		if dirname == "Batting":
			df_combined['playerid'] = df_combined['batter']
		if dirname == "Pitching":
			df_combined['playerid'] = df_combined['pitcher']
		df_combined['play_id'] = df_combined['Rk.']
		df_combined['barrel'] = df_combined['launch_speed_angle']
		df_combined['barrel'] = np.where(df_combined['launch_speed_angle'] >= 1, 0, df_combined['barrel'])
		df_combined['barrel'] = np.where(df_combined['launch_speed_angle'] == 6, 1, df_combined['barrel'])
		df_combined['adj_xSLG'] = df_combined['xSLG']
		df_combined['adj_xwOBA'] = df_combined['xwOBA']
		df_combined['adj_xBA'] = df_combined['xBA']
		df_combined['barrel'] = np.where(df_combined['Result'] == "strikeout", 0, df_combined['barrel'])
		df_combined['barrel'] = np.where(df_combined['Result'] == "strikeout_double_play", 0, df_combined['barrel'])
		df_combined['adj_xSLG'] = np.where(df_combined['Result'] == "strikeout", 0, df_combined['adj_xSLG'])
		df_combined['adj_xSLG'] = np.where(df_combined['Result'] == "strikeout_double_play", 0, df_combined['adj_xSLG'])
		df_combined['adj_xBA'] = np.where(df_combined['Result'] == "strikeout", 0, df_combined['adj_xBA'])
		df_combined['adj_xBA'] = np.where(df_combined['Result'] == "strikeout_double_play", 0, df_combined['adj_xBA'])
		df_combined['isBB'] = np.where(df_combined['Result'] == "walk", 1, 0)
		df_combined['isK'] = np.where(df_combined['Result'] == "strikeout", 1, 0)
		df_combined['isK'] = np.where(df_combined['Result'] == "strikeout_double_play", 1, df_combined['isK'])
		df_combined['isHR'] = np.where(df_combined['Result'] == "home_run", 1, 0)
		df_combined['is1b'] = np.where(df_combined['Result'] == "single", 1, 0)
		df_combined['is2b'] = np.where(df_combined['Result'] == "double", 1, 0)
		df_combined['is3b'] = np.where(df_combined['Result'] == "triple", 1, 0)
		df_combined['isgidp'] = np.where(df_combined['Result'] == "grounded_into_double_play", 1, 0)
		df_combined['points'] = df_combined['iso_value'] + df_combined['babip_value'] + df_combined['isBB'] - \
		                        df_combined['isK'] + df_combined['isHR']
		df_combined['xPoints'] = df_combined['adj_xSLG']
		df_combined['xPoints'] = np.where(df_combined['Result'] == "walk", 1, df_combined['xPoints'])
		df_combined['xPoints'] = np.where(df_combined['Result'] == "strikeout", -1, df_combined['xPoints'])
		df_combined['xPoints'] = np.where(df_combined['Result'] == "strikeout_double_play", -1, df_combined['xPoints'])

		# points = iso_value + babip_value + isBB - isK + isHR
		# print(df_combined.columns)

		df_rows = len(df_combined)
		print("Number of rows collected: " + str(df_rows))

		# if table exists -
		#    - if no rows for GameDate, insert
		#    - if num_rows not equal to rows in table on GameDate, delete and insert
		#    - if num_rows equal to num rows in table for GameDate, skip
		# if table does not exist, insert
		if table_exists(tablename):
			print(tablename + " exists")
			tablerows = game_date_rows(tablename, dt8)
			df_combined.rename(columns={df_combined.columns[0]: "pitch_type"}, inplace=True)
			colname = df_combined.columns[0]
			print("First column name: " + colname)
			print("Table for date has " + str(tablerows) + " rows")
			if tablerows == 0:
				print("No rows in table. Insert")
				delete_cmd = "DELETE from " + tablename + " where game_date = '" + dt + "'"
				print(delete_cmd)
				not_run = True
				tries = 0
				max_tries = 3
				while not_run and tries < max_tries:
					try:
						bdb.delete(delete_cmd)
						df_combined.to_sql(tablename, bdb.conn, if_exists='append', index=False)
						not_run = False
					except Exception as ex:
						print(str(ex))
						tries += 1
						time.sleep(2.5)
				if not_run:
					"DB Update failed: " + tablename
				else:
					"DB Update succeeded: " + tablename
			else:
				if df_rows == tablerows and override is False:
					print("Rows match, skip ...")
				else:
					print("Rows don't match or override chosen, delete and insert")
					delete_cmd = "DELETE from " + tablename + " where game_date = '" + dt + "'"
					print(delete_cmd)
					time.sleep(4)
					try:
						bdb.delete(delete_cmd)
						time.sleep(1)
						df_combined.to_sql(tablename, bdb.conn, if_exists='append', index=False)
					except Exception as ex:
						print(str(ex))
		else:
			print(tablename + " does not exist. Insert")
			try:
				df_combined.to_sql(tablename, bdb.conn, if_exists='append', index=False)
			except Exception as ex:
				print(str(ex))

		return_value = df_combined

	update_cmd = "update " + tablename + " set play_id = play_id + " + str(int(dt8) * 10000) + \
	             " where game_date = '" + str(dt) + "'"
	bdb.update(update_cmd)

	return return_value


def table_exists(table):
	cmd = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='" + table + "'"
	c = bdb.select(cmd)
	return c[0][0]


def game_date_rows(tablename, dt8):
	cmd = "SELECT count(*) FROM " + tablename + " WHERE gamedate = " + dt8
	c = bdb.select(cmd)
	return int(c[0][0])

#
# def get_one_day(f, dt_, year_, player_type, print_header=0):
# 	# https://baseballsavant.mlb.com/statcast_search/csv?
#
# 	url_csv_text = "/csv?all=true&"
#
# 	url_base = "https://baseballsavant.mlb.com/statcast_search"
#
# 	url_basic_search_text = "?"
#
# 	url_body = "hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%" \
# 	           "7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%" \
# 	           "7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7C" \
# 	           "fielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7C" \
# 	           "force%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7C" \
# 	           "sac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7C" \
# 	           "sac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%" \
# 	           "7Ctriple%5C.%5C.play%7C&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=" \
# 	           "&hfC=&hfSea=" + str(year_) + "%7C&hfSit=&player_type=" \
# 	           + player_type + "&hfOuts=&opponent=&" \
# 	                           "pitcher_throws=&batter_stands=&hfSA=&game_date_gt=" + dt_ + \
# 	           "&game_date_lt=" + dt_ + \
# 	           "&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&" \
# 	           "min_results=0&group_by=name-event&sort_col=xwoba&player_event_sort=api_p_release_speed&" \
# 	           "sort_order=desc&min_pas=0"
#
# 	url_checks = "&chk_event_launch_speed=on&" \
# 	             "chk_event_launch_angle=on&" \
# 	             "chk_event_release_spin_rate=on&" \
# 	             "chk_event_release_speed=on&" \
# 	             "chk_event_hit_distance_sc=on&" \
# 	             "chk_event_estimated_ba_using_speedangle=on&" \
# 	             "chk_event_estimated_slg_using_speedangle=on&" \
# 	             "chk_event_estimated_woba_using_speedangle=on"
#
# 	url_details = "&type=details&"
# 	url_footer = "#results"
#
# 	url_details_text = url_base + url_csv_text + url_body + url_checks + url_details
# 	url_text = url_base + url_basic_search_text + url_body + url_checks + url_footer
#
# 	print(url_details_text)
# 	print(url_text)
#
# 	print("sleeping ....")
# 	time.sleep(1)
#
# 	page = requests.get(url_text)
# 	soup = BeautifulSoup(page.content, 'html.parser')
#
# 	if print_header:
# 		count = 0
# 		line_str = ""
# 		for item in soup.find_all('th'):
# 			count += 1
# 			line_str += (item.get_text() + ',')
# 		line_str = line_str[:-1]
# 		# line_str += "extra,"
# 		if count > 0:
# 			f.write(line_str.strip())
# 			f.write("\n")
#
# 	count = 0
# 	line_str = ""
# 	for item in soup.find_all('td'):
# 		if item.find('span'):
# 			line_str = line_str[:-1]
# 			data = line_str.strip()
# 			if len(data):
# 				f.write(data)
# 				f.write("\n")
# 				count = 0
# 				line_str = ""
# 		if item.get('class'):
# 			count += 1
# 			text = str(item.get_text().strip())
# 			if text == dt_:
# 				text = text.replace('-', '')
# 			line_str += text + ','
# 		if item.get('id'):
# 			playerid = str(item['id'][3:])
# 			count += 1
# 			line_str += playerid + ','
#
# 	line_str = line_str[:-1]
# 	print(line_str.strip())
# 	if count > 0:
# 		f.write(line_str.strip())
# 		f.write("\n")
#
# 	return count


# noinspection PyTypeChecker
# def post_process_csv_file(infile, outfile):
# 	df = pd.read_csv(infile, encoding='unicode_escape')
#
# 	# Drop unnamed column
# 	# df = df.drop(df.columns[[1]], axis=1)
#
# 	# Set header names
# 	print("df head")
# 	colnames = list(df.columns)
# 	colnames.insert(3, 'playerid')
# 	del colnames[1]
# 	colnames[6] = "LaunchAngle"
# 	colnames[-1] = "Adj_xWOBA"
#
# 	# colnames.pop()
# 	print(colnames)
# 	print("---")
#
# 	df.columns = colnames
#
# 	df['Adj_xSLG'] = df['xSLG']
# 	print("df columns:")
# 	print(df.columns)
# 	print("-----")
#
# 	df.to_csv(outfile, index=False)


def single_year(year, bp, dates=(3, 18, 3, 28)):
	###################
	###################
	# Hard coded:
	sleep_interval = .5
	season = year
	start_m = dates[0]
	start_d = dates[1]
	end_m = dates[2]
	end_d = dates[3]
	# bp = "bat" or "pitch"

	#  END HARD CODE
	####################
	###################

	bpdir = "Batting"
	if bp == "pitch":
		bpdir = "Pitching"

	player_type = "batter"
	if bp == "pitch":
		player_type = "pitcher"

	start_dt = date(season, start_m, start_d)
	end_dt = date(season, end_m, end_d)

	year = str(season)

	for dt in daterange(start_dt, end_dt):
		df = single_day(date=dt, year=year, player_type=player_type, dir=bpdir, override=True)
		time.sleep(sleep_interval)

		filename = bpdir + "_events_combined_daily.csv"
		outfile = data_dir / filename

		# outfile = "C:\\Users\chery\Documents\BBD\Statcast\\" + bpdir + "\\" + "events_combined_daily.csv"
		if isinstance(df, pd.DataFrame):
			df.to_csv(outfile, index=False)
		dt8 = int(str.replace(str(dt), "-", ""))
		print("Date8: " + str(dt8))

	# Cleanup
	bdb.update(
		"update StatcastBattingEvents set xBA = 0, adj_xBA = 0, hit_distance_sc = 0, xwOBA = 0, "
		"xSLG = 0, adj_xwOBA = 0, adj_xSLG = 0 where xwOBA is NULL and events like 'strikeout%'")
	bdb.update(
		"update StatcastPitchingEvents set xBA = 0, adj_xBA = 0, hit_distance_sc = 0, xwOBA = 0, "
		"xSLG = 0, adj_xwOBA = 0, adj_xSLG = 0 where xwOBA is NULL and events like 'strikeout%'")
	bdb.update(
		"update StatcastBattingEvents set xwOBA = 0.69, xSLG = NULL, "
		"adj_xwOBA = 0.69, adj_xSLG = NULL where events = 'walk'")
	bdb.update(
		"update StatcastPitchingEvents set xwOBA = 0.69, xSLG = NULL,"
		" adj_xwOBA = 0.69, adj_xSLG = NULL where events = 'walk'")


def main():
	# single_year(2016, "bat", (5, 1, 5, 1))
	# single_year(2016, "pitch")
	today = date.today()
	yest = today - timedelta(days=1)
	past = today - timedelta(days=2)

	for year in [2022]:
		for bp in ["bat", "pitch"]:
			#single_year(year, bp, (6, 4, 6, 4))
			single_year(year, bp, (past.month, past.day, yest.month, yest.day))


if __name__ == "__main__":
	main()
