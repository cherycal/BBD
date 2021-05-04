__author__ = 'chance'

import csv
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path

#bdb = sqldb.DB('Baseball.db')
# c = bdb.select("SELECT * FROM Leagues")
#
# for t in c:
#     print(t)
#
#bdb.close()
# exit(0)

year = "2021"
# Custom statcast stats
url = "https://baseballsavant.mlb.com/leaderboard/custom?year=" + \
      year + "&type=batter&filter=&sort=1&sortDir=desc&min=1&selections=" + \
      "player_id,player_age,b_ab,b_total_pa,b_single,b_double,b_triple,b_home_run," + \
      "b_strikeout,b_walk,batting_avg,slg_percent,on_base_percent,b_rbi,r_total_stolen_base," + \
      "xba,xslg,xwoba,xobp,exit_velocity_avg,launch_angle_avg,sweet_spot_percent," + \
      "barrel_batted_rate,oz_swing_percent,oz_contact_percent,iz_contact_percent," + \
      "&chart=false&x=player_age&y=player_age&r=no&chartType=beeswarm&csv=true"

# Default statcast expected stats
# url = https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=batter&year=2020&position=&team=&min=1&csv=true


# print(urllib.request.urlopen(url).read().decode(urllib.request.urlopen(url).headers.get_content_charset('utf-8')))
# or ...

print(url)

response = urllib.request.urlopen(url)
html_response = response.read()
encoding = response.headers.get_content_charset('utf-8')
decoded_html = html_response.decode(encoding)

# print(decoded_html)


csv_filename = "C:\\Users\\chery\\Documents\\BBD\\Statcast\\Batting\\" + year + "batting_season.csv"
f = open(csv_filename, "w")
f.write(decoded_html)
f.close()
