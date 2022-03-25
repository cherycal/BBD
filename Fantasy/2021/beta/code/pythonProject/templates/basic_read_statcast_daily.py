__author__ = 'chance'

import sys

sys.path.append('../modules')
import pandas as pd
import time
import push

inst = push.Push()

import sqldb
bdb = sqldb.DB('Baseball.db')

def main():
	url_text = "https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7C&hfC=&hfSea=2021%7C&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2021-04-01&game_date_lt=2021-04-02&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfPull=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-date&sort_col=xwoba&player_event_sort=api_h_launch_speed&sort_order=desc&min_pas=0&chk_stats_date=on&chk_stats_player_id=on&chk_stats_pa=on&chk_stats_abs=on&chk_stats_bip=on&chk_stats_hits=on&chk_stats_singles=on&chk_stats_dbls=on&chk_stats_triples=on&chk_stats_hrs=on&chk_stats_so=on&chk_stats_k_percent=on&chk_stats_bb=on&chk_stats_bb_percent=on&chk_stats_babip=on&chk_stats_iso=on&chk_stats_ba=on&chk_stats_xba=on&chk_stats_xbadiff=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xslgdiff=on&chk_stats_obp=on&chk_stats_xobp=on&chk_stats_woba=on&chk_stats_xwoba=on&chk_stats_wobadiff=on&chk_stats_velocity=on&chk_stats_launch_speed=on&chk_stats_launch_angle=on&chk_stats_bbdist=on&chk_stats_spin_rate=on&chk_stats_plate_x=on&chk_stats_plate_z=on&chk_stats_release_pos_x=on&chk_stats_release_pos_z=on&chk_stats_pos3_int_start_distance=on&chk_stats_pos4_int_start_distance=on&chk_stats_pos6_int_start_distance=on&chk_stats_pos5_int_start_distance=on&chk_stats_pos7_int_start_distance=on&chk_stats_pos8_int_start_distance=on&chk_stats_pos9_int_start_distance=on&chk_stats_release_extension=on#results"

	print(url_text)

	print("sleeping ....")
	time.sleep(1)

	csvfile = "statcast_daily_test.csv"

	# "C:\\Users\\chery\\Documents\\BBD\\FG\\" + bpdir + "\\" + "events_daily.csv"

	df = pd.read_html(url_text)[0]

	df.drop(df.columns[[1,7,-1]], axis=1, inplace=True)
	df.columns.values[6] = "id"
	df['Date'] = pd.to_datetime(df['Date'])
	df['Date'] = df['Date'].dt.strftime('%Y%m%d')
	df.insert(loc=2, column='playerid', value=df['id'])
	df.drop(['id'], axis=1, inplace=True)

	bpdir = "Pitching"
	df.to_csv(csvfile, index=False, encoding = 'utf-8-sig')
	table_name = "Statcast" + bpdir + "Daily"
	df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


	print("done")


if __name__ == "__main__":
	main()
