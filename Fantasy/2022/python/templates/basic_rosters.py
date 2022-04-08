__author__ = 'chance'
import sys
sys.path.append('../modules')
import sqldb

# My python class: sqldb.py

mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')

#c = bdb.select("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ESPNPlayerDataCurrent'")
r = bdb.select_plus("SELECT * FROM ESPNRostersWithMLBID")

roster = dict()
teams = dict()

for d in r['dicts']:
    if teams.get(d['MLBID']):
        #print(d['MLBID'], f'{d["Team"][0:6]} 1 {d["Position"]}')
        teams[d['MLBID']].append(f'{d["Team"][0:6]} {d["Position"]}')
    else:
        #print(d['MLBID'], f'{d["Team"][0:6]} 2 {d["Position"]}')
        teams[d['MLBID']] = list()
        teams[d['MLBID']].append(f'{d["Team"][0:6]} {d["Position"]}')

for player in teams:
    if player == 665862:
        print(f'{player}: {teams[player]}')

bdb.close()
