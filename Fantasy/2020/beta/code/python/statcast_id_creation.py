__author__ = 'chance'

import csv
import os
import sys
import time
import urllib.request
from datetime import datetime
import pandas as pd

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path

bdb = sqldb.DB('Baseball.db')
# c = bdb.select("SELECT * FROM Leagues")
#
# for t in c:
#     print(t)
#
bdb.close()


# exit(0)


def write_file(url, csv_filename, flag):
	print(url)

	response = urllib.request.urlopen(url)
	html_response = response.read()
	encoding = response.headers.get_content_charset('utf-8')
	decoded_html = html_response.decode(encoding)

	# print(decoded_html)

	f = open(csv_filename, flag)
	f.write(decoded_html)
	f.write("\n")
	f.close()


csv_file = "C:\\Users\\chery\\Documents\\BBD\\Statcast\\Metadata\\ids.csv"

url_name = "https://baseballsavant.mlb.com/leaderboard/custom?year=2020,2019,2018,2017&type=batter" + \
           "&filter=&sort=1&sortDir=desc&min=1&selections=player_id,b_ab,&chart=false" + \
           "&x=b_ab&y=b_ab&r=no&chartType=beeswarm&csv=true"

write_file(url_name, csv_file, "w")

url_name = "https://baseballsavant.mlb.com/leaderboard/custom?year=2020&type=pitcher" + \
           "&filter=&sort=1&sortDir=desc&min=1&selections=player_id,p_total_pa,&chart=false" + \
           "&x=b_ab&y=b_ab&r=no&chartType=beeswarm&csv=true"

write_file(url_name, csv_file, "a")

df = pd.read_csv(csv_file)
df['Name'] = df[' first_name'] + " " + df['last_name']
df['Name'] = df['Name'].str.strip()

dfids = df[['Name', 'player_id']].copy()

dfids.sort_values("Name", inplace=True)
dfids.drop_duplicates(subset='player_id', keep="first", inplace=True)

dfids.to_csv(csv_file, index=False)
