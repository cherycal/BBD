__author__ = 'chance'

import json
import os
import sys
import time
import urllib.request
from datetime import datetime
import pandas as pd

sys.path.append('./modules')
from bs4 import BeautifulSoup
import requests
import pandas as pd
import tools
import time
import push
from datetime import timedelta, datetime, date

inst = push.Push()

import sqldb
bdb = sqldb.DB('Baseball.db')


def daterange(date1, date2):
	for n in range(int((date2 - date1).days) + 1):
		yield date1 + timedelta(n)


# https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2019%7C&hfSit=&player_type=batter&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2019-07-17&game_date_lt=2019-07-17&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-event&sort_col=xwoba&player_event_sort=api_p_release_speed&sort_order=desc&min_pas=0&chk_event_launch_speed=on


# Pitch speed and spin rate
# &chk_event_release_spin_rate=on&chk_event_release_speed=on#results

def get_one_day(f, dt_, year_, player_type, print_header=0):
	url_text = "https://baseballsavant.mlb.com/statcast_search?" \
	           "hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%" \
	           "7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%" \
	           "7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7C" \
	           "fielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7C" \
	           "force%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7C" \
	           "sac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7C" \
	           "sac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%" \
	           "7Ctriple%5C.%5C.play%7C&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7C" \
	           "&hfC=&hfSea=" + str(year_) + "%7C&hfSit=&player_type=" + player_type + "&hfOuts=&opponent=&" \
	                                                                                   "pitcher_throws=&batter_stands=&hfSA=&game_date_gt=" + dt_ + \
	           "&game_date_lt=" + dt_ + \
	           "&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfPull=&metric_1=&hfInn=&min_pitches=0&" \
	           "min_results=0&group_by=name-date&sort_col=xwoba&player_event_sort=api_h_launch_speed&" \
	           "sort_order=desc&min_pas=0" \
	           "&chk_stats_pa=on" \
	           "&chk_stats_player_id=on" \
	           "&chk_stats_abs=on" \
	           "&chk_stats_bip=on" \
	           "&chk_stats_hits=on" \
	           "&chk_stats_singles=on" \
	           "&chk_stats_dbls=on" \
	           "&chk_stats_triples=on" \
	           "&chk_stats_hrs=on" \
	           "&chk_stats_so=on" \
	           "&chk_stats_k_percent=on" \
	           "&chk_stats_bb=on" \
	           "&chk_stats_bb_percent=on" \
	           "&chk_stats_babip=on" \
	           "&chk_stats_iso=on" \
	           "&chk_stats_ba=on" \
	           "&chk_stats_xba=on" \
	           "&chk_stats_xbadiff=on" \
	           "&chk_stats_slg=on" \
	           "&chk_stats_xslg=on" \
	           "&chk_stats_xslgdiff=on" \
	           "&chk_stats_obp=on" \
	           "&chk_stats_xobp=on" \
	           "&chk_stats_woba=on" \
	           "&chk_stats_xwoba=on" \
	           "&chk_stats_wobadiff=on" \
	           "&chk_stats_velocity=on" \
	           "&chk_stats_launch_speed=on" \
	           "&chk_stats_launch_angle=on" \
	           "&chk_stats_bbdist=on" \
	           "&chk_stats_spin_rate=on" \
	           "&chk_stats_plate_x=on" \
	           "&chk_stats_plate_z=on" \
	           "&chk_stats_release_pos_x=on" \
	           "&chk_stats_release_pos_z=on" \
	           "&chk_stats_pos3_int_start_distance=on" \
	           "&chk_stats_pos4_int_start_distance=on" \
	           "&chk_stats_pos6_int_start_distance=on" \
	           "&chk_stats_pos5_int_start_distance=on" \
	           "&chk_stats_pos7_int_start_distance=on" \
	           "&chk_stats_pos8_int_start_distance=on" \
	           "&chk_stats_pos9_int_start_distance=on" \
	           "&chk_stats_release_extension=on" \
	           "#results"

	print(url_text)

	print("sleeping ....")
	time.sleep(1)
	bpdir = "Batting"
	if player_type == "pitcher":
		bpdir = "Pitching"

	csvfile = "C:\\Users\\chery\\Documents\\BBD\\Statcast\\" + bpdir + "\\" + "events_daily.csv"

	df = pd.read_html(url_text)[0]
	df.to_csv(csvfile, index=False)


	print("done")


# noinspection PyTypeChecker
def post_process_csv_file(infile, outfile):
	# header = ["Rank", "Player", "Id", "Date", "Pitches", "Total", "PitchPct",
	#       "PA", "AB", "KPct", "BBPct", "SLG", "xSLG", "wOBA", "xwOBA", "EV"]

	df = pd.read_csv(infile, encoding='unicode_escape')

	# Drop unnamed column
	df = df.drop(df.columns[[1]], axis=1)

	# Set header names
	print("df head")
	colnames = list(df.columns)
	colnames.insert(2, 'playerid')
	colnames.pop()
	print(colnames)
	print("---")

	df.columns = colnames

	# df['SO'] = round(df['PA'] * df['K%'] / 100, 0)
	# df['BB'] = round(df['PA'] * df['BB%'] / 100, 0)

	print("df columns:")
	print(df.columns)
	print("-----")

	df.to_csv(outfile, index=False)


def main():
	###################
	###################
	# Hard coded:
	sleep_interval = .5
	season = 2021
	start_m = 4
	start_d = 1
	end_m = 4
	end_d = 1

	# bp = "bat" or "pitch"
	bp = "pitch"

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

	# year = str(season)
	# raw_outfile = "C:\\Users\\chery\\Documents\\BBD\\Statcast\\" + bpdir + "\\" + year + bp + "_raw.csv"

	f = open(raw_outfile, "w")
	total_rows = 0
	for dt in daterange(start_dt, end_dt):
		# print_header = 1
		# if total_rows > 0:
		# 	print_header = 0
		get_one_day(f, dt.strftime("%Y-%m-%d"), season, player_type, print_header)
		time.sleep(sleep_interval)

	# print()
	# print(raw_outfile + " complete")
	# f.close()
	#
	# outfile = "C:\\Users\chery\Documents\BBD\Statcast\\" + bpdir + "\\" + year + bp + "_daily.csv"
	# post_process_csv_file(raw_outfile, outfile)
	#
	# table_name = "Statcast" + bpdir + "Daily"
	#
	# df = pd.read_csv(outfile)
	# df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
	#
	# exit(0)


if __name__ == "__main__":
	main()
