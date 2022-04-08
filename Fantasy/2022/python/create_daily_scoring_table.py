__author__ = 'chance'

import sys

import pandas as pd

sys.path.append('./modules')
import fantasy

# My python class: sqldb.py

mode = "PROD"
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()

# PROD DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')
# TEST DB location: ('C:\\Ubuntu\\Shared\\data\\BaseballTest.db')

# From DB
# def get_statid_dict():
# 	return_dict = {}
# 	rows = bdb.select("SELECT statid, statabbr from ESPNStatIds")
# 	for row in rows:
# 		return_dict[row[0]] = row[1]
# 	return return_dict
#
# statid_dict = get_statid_dict()
#
# for statid in statid_dict:
# 	print(str(statid) + ": " + str(statid_dict[statid]))

###########################
# From module

statid_dict = fantasy.get_statid_dict()
lol = []
statcats = ['Name','playerid','date','points','leagueId','teamId','lineupSlotId']
numlist = ['',0,0,0,0,0,0]

for statid in statid_dict:
	print(str(statid) + "-> " + str(statid_dict[statid]))
	statcats.append(str(statid_dict[statid]))
	numlist.append(0.0)

lol.append(numlist)

df = pd.DataFrame(lol, columns=statcats)

table_name = "ESPNDailyScoring"
df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

bdb.close()
