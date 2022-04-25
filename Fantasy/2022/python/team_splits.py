__author__ = 'chance'

import sys

sys.path.append('./modules')
import pandas as pd
import time
import push
from pathlib import Path
from datetime import datetime

p = Path.cwd()
data_dir = p / 'data'
data_dir.mkdir(mode=0o755, exist_ok=True)

inst = push.Push()

import sqldb

bdb = sqldb.DB('Baseball.db')

now = datetime.now()

date8 = now.strftime("%Y%m%d")


def do_splits(split_name, yr):
	month = 0
	if split_name == "Left":
		month = 13
	elif split_name == "Right":
		month = 14
	elif split_name == "Home":
		month = 15
	elif split_name == "Away":
		month = 16
	else:
		print("Split name must be 'Left','Right','Home', or 'Away'")
		exit(-1)

	url_text = "https://www.fangraphs.com/leaders.aspx?pos=all" \
	           "&stats=bat&lg=all&qual=0&type=1&season=" + str(yr) + \
	           "&month=" + str(month) + "&season1=" + str(yr) + \
	           "&ind=0&team=0,ts&rost=0&age=0&filter=&players=0&startdate=" + \
	           str(yr) + "-01-01&enddate=" + str(yr) + "-12-31&sort=15,d"

	# "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat" \
	# "&lg=all&qual=0&type=1&season=2021&month=14" \
	# "&season1=2021&ind=0&team=0,ts&rost=0&age=0&filter=&players=0"

	print(url_text)

	print("sleeping 25 ....")
	time.sleep(25)

	# csvfile = "C:\\Users\\chery\\Documents\\BBD\\FG\\Batting\\" + \
	#           "team_splits_" + split_name + "_" + str(yr) + ".csv"

	csvfile = data_dir / str("team_splits_" + split_name + "_" + str(yr) + ".csv")

	tbl_array = pd.read_html(url_text, attrs={'id': 'LeaderBoard1_dg1_ctl00'}, header=1)



	df = tbl_array[0]
	df.drop(df.tail(1).index, inplace=True)
	df['Vs'] = split_name.upper()
	df['Year'] = yr
	df['updatedate'] = date8
	df = df.rename(columns={'#': 'Rank'})
	print(df.columns)
	df.to_csv(csvfile, index=False)
	print(csvfile)

	table_name = "TeamSplits"
	tbl_exists = False

	tbltest = bdb.select("SELECT name FROM sqlite_master WHERE type='table' AND name='" +
	                     table_name + "'")
	if len(tbltest) > 0:
		tbl_exists = True

	if tbl_exists:
		delete_cmd = "DELETE from " + table_name + " where Vs = '" + \
		             split_name.upper() + "' and Year = " + str(yr)
		print(delete_cmd)
		bdb.delete(delete_cmd)

	df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

	# Conform to MLB abbreviations
	bdb.update("Update TeamSplits set Team = 'WSH' where Team = 'WSN'")
	bdb.update("Update TeamSplits set Team = 'SF' where Team = 'SFG'")
	bdb.update("Update TeamSplits set Team = 'SD' where Team = 'SDP'")
	bdb.update("Update TeamSplits set Team = 'KC' where Team = 'KCR'")

	bdb.cmd("INSERT INTO TeamSplitsHistory SELECT * FROM TeamSplits", True)

	print("done")


def main():
	yr = 2022
	for lr in ["Left", "Right", "Home", "Away"]:
		do_splits(lr, yr)


if __name__ == "__main__":
	main()
