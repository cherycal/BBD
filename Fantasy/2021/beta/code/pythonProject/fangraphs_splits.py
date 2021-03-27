__author__ = 'chance'

import sys
import numpy as np
import pandas as pd


sys.path.append('./modules')
import requests
from bs4 import BeautifulSoup as bs
import tools
import time
import push
import sqldb

inst = push.Push()
from urllib.parse import unquote
import csv

sleep_interval = 40

bat_pitch = "Batting"
left_right = "Left"
from_yr = 2014
to_yr = 2020
stat_group = 2

bat_pitch_indicator = "B"
left_right_indicator = 1
left_right_id = "L"
filter_indicator = "PA"

if left_right == "Right":
	left_right_indicator = 2
	left_right_id = "R"

if bat_pitch == "Pitching":
	bat_pitch_indicator = "P"
	left_right_indicator = 5
	left_right_id = "L"
	filter_indicator = "IP"
	if left_right == "Right":
		left_right_indicator = 6
		left_right_id = "R"

# &statgroup=:

#		1: Standard
#		2: Advanced
#		3: Batted Balls

# vs LHP: splitArr=1
# vs RHP: splitArr=2
# Min plate appearances ( Number after the last %7C - 1 in this example ) : &filter=PA%7Cgt%7C1

# Multiple seasons, grouped by season: https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=1&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=player&statgroup=1&startDate=2018-03-01&endDate=2020-11-01&players=&filter=&groupBy=season&sort=-1,1
# Pitching: https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=&splitArrPitch=&position=P&autoPt=false&splitTeams=false&statType=player&statgroup=1&startDate=2018-03-01&endDate=2020-11-01&players=&filter=&groupBy=season&sort=-1,1

url = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=" + str(left_right_indicator) + \
      "&splitArrPitch=&position=" + bat_pitch_indicator + "&autoPt=true&splitTeams=false&statType=player&statgroup=" + \
      str(stat_group) + "&startDate=" + str(from_yr) + "-03-01&endDate=" + str(to_yr) + \
      "-11-01&players=&filter=" + filter_indicator + "%7Cgt%7C1&groupBy=season&sort=-1,1"

# Selenium
driver = tools.get_driver("headless")
driver.get(url)
time.sleep(sleep_interval)
html = driver.page_source

soup = bs(html, "html.parser")
results = soup.find_all('a', attrs={"class": "data-export"})

print(url)
print(results)

raw_data = results[0]['href']
data_list = raw_data.split(",")

my_csv = unquote(data_list[1])
print(type(my_csv))

csv_filename = "C:\\Users\\chery\\Documents\\BBD\\FG\\" + bat_pitch + "\\" + \
               "season_splits_" + left_right + "_" + str(stat_group) + "_" + \
				str(from_yr) + "-" + str(to_yr) + ".csv"

new_csv = ""
count = 0
for line in my_csv.split('\n'):
	if count == 0:
		print("x")
		print(line)
		print(type(line))
		line = line.replace('%', 'Pct')
		line = line.replace('/', 'Per')
		line = line.replace('+', 'Plus')
		new_csv += line + ",BatPitch,Vs,\n"
		print(line)
	else:
		new_csv += line + "," + bat_pitch_indicator + "," + left_right + '\n'
	count += 1


#print(new_csv)

f = open(csv_filename, "w")
f.write(new_csv)
f.close()

bdb = sqldb.DB('Baseball.db')
table_name = "FG" + bat_pitch + "SplitsSimple"

df = pd.read_csv(csv_filename)
df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
bdb.close()

driver.close()
