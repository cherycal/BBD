__author__ = 'chance'

import sys

import pandas as pd

sys.path.append('./modules')
from bs4 import BeautifulSoup as bs
import tools
import time
import push
import sqldb
from pathlib import Path
from datetime import datetime

now = datetime.now()

date8 = now.strftime("%Y%m%d")

p = Path.cwd()
data_dir = p / 'data'
data_dir.mkdir(mode=0o755, exist_ok=True)

inst = push.Push()
from urllib.parse import unquote


bdb = sqldb.DB('Baseball.db')
driver = tools.get_driver()

def do_split(bat_pitch, left_right, from_yr, to_yr):
	# Selenium
	#driver = tools.get_driver("headless")

	sleep_interval = 15

	#
	# bat_pitch = "Batting"
	# left_right = "Right"
	# from_yr = 2021
	# to_yr = 2021

	stat_group = 2
	# &statgroup=:
	# 1: Standard
	# 2: Advanced
	# 3: Batted Balls

	bat_pitch_indicator = bat_pitch[0]
	# left_right_id = left_right[0]

	left_right_indicator = 0
	filter_indicator = ""

	if bat_pitch == "Batting":
		filter_indicator = "PA"
		if left_right == "Left":
			left_right_indicator = 1
		elif left_right == "Right":
			left_right_indicator = 2
		else:
			print("Left right indicator must be Left or Right")
			exit(-1)
	elif bat_pitch == "Pitching":
		filter_indicator = "IP"
		if left_right == "Left":
			left_right_indicator = 5
		elif left_right == "Right":
			left_right_indicator = 6
		else:
			print("Left/Right indicator must be Left or Right")
			exit(-1)
	else:
		print("Bat/Pitch indicator must be Left or Right")
		exit(-1)

	# vs LHP: splitArr=1
	# vs RHP: splitArr=2
	# Min plate appearances ( Number after the last %7C - 1 in this example ) : &filter=PA%7Cgt%7C1

	# Multiple seasons, grouped by season: https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=1&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=player&statgroup=1&startDate=2018-03-01&endDate=2020-11-01&players=&filter=&groupBy=season&sort=-1,1
	# Pitching: https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=&splitArrPitch=&position=P&autoPt=false&splitTeams=false&statType=player&statgroup=1&startDate=2018-03-01&endDate=2020-11-01&players=&filter=&groupBy=season&sort=-1,1

	url = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=" + str(left_right_indicator) + \
	      "&splitArrPitch=&position=" + bat_pitch_indicator + "&autoPt=true&splitTeams=false&statType=player&statgroup=" + \
	      str(stat_group) + "&startDate=" + str(from_yr) + "-03-01&endDate=" + str(to_yr) + \
	      "-11-01&players=&filter=" + filter_indicator + "%7Cgt%7C1&groupBy=season&sort=-1,1"

	not_loaded = True
	raw_data = ""

	while not_loaded:
		print(url)
		try:
			print(f'Sleep for {sleep_interval}')
			time.sleep(sleep_interval)
			driver.get(url)
			html = driver.page_source
			print(f'Sleep for {sleep_interval}')
			time.sleep(sleep_interval)
			soup = bs(html, "html.parser")
			print(f'Sleep for {sleep_interval}')
			time.sleep(sleep_interval)
			results = soup.find_all('a', attrs={"class": "data-export"})
			if not len(results):
				print(results)
			raw_data = results[0]['href']
			not_loaded = False
		except Exception as ex:
			print("Retrieval failed: " + str(ex))
			sleep_interval += 5  # sleep longer if page doesn't load
			print(f'Sleep for {sleep_interval}')
			time.sleep(sleep_interval)

	data_list = raw_data.split(",")
	my_csv = unquote(data_list[1])
	#print(type(my_csv))

	# csv_filename = "C:\\Users\\chery\\Documents\\BBD\\FG\\" + bat_pitch + "\\" + \
	#                "season_splits_" + left_right + "_" + str(stat_group) + "_" + \
	#                str(from_yr) + "-" + str(to_yr) + ".csv"

	csv_filename = data_dir / str("season_splits_" + left_right + \
	                              "_" + str(stat_group) + "_" + \
	                              str(from_yr) + "-" + str(to_yr) + ".csv")

	# df = pd.read_html(url)[0]
	# df.to_csv(csvfile, index=False)

	new_csv = ""
	count = 0
	for line in my_csv.split('\n'):
		if count == 0:
			#print(line)
			#print(type(line))
			line = line.replace('%', 'Pct')
			line = line.replace('/', 'Per')
			line = line.replace('+', 'Plus')
			new_csv += line + ",BatPitch,Vs,updatedate\n"
			#print(line)
		else:
			new_csv += line + "," + bat_pitch_indicator + "," + left_right + "," + str(date8) + '\n'
		count += 1

	# print(new_csv)

	f = open(csv_filename, "w")
	f.write(new_csv)
	f.close()

	table_name = "FG" + bat_pitch + "SplitsSimple"

	delete_cmd = "DELETE from " + table_name + " where BatPitch = '" + bat_pitch_indicator + "'" + \
	             " and Season = " + str(from_yr) + " and Vs = '" + left_right + "'"

	try:
		print(delete_cmd)
		bdb.delete(delete_cmd)

		df = pd.read_csv(csv_filename)

		for column in df[['AVG', 'BABIP', 'BBPct', 'BBPerK', 'wOBA','wRCPlus','wRC','wRAA','ISO','KPct','OBP','OPS','SLG']]:
			df[column] = round(df[column],4)

		df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
	except Exception as ex:
		print(str(ex))

	#driver.close()


def main():
	from_yr = 2022
	to_yr = 2022
	for left_right in ["Left", "Right"]:
		for bat_pitch in ["Batting", "Pitching"]:
			do_split(bat_pitch, left_right, from_yr, to_yr)

	bdb.close()


if __name__ == "__main__":
	main()
