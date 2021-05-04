__author__ = 'chance'

from bs4 import BeautifulSoup
import time
import json
import os
import sys
import time
import urllib.request
import pandas as pd
sys.path.append('./modules')
import sqldb

# My python class: sqldb.py

bdb = sqldb.DB('Baseball.db')

league = 162788
year = 2021
addr = "https://fantasy.espn.com/apis/v3/games/flb/seasons/" + "2020" + \
       "/segments/0/leagues/" + str(league) + \
       "?view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions&" + \
       "view=mPositionalRatings&view=mRoster&view=mSettings&view=mTeam&view=modular&view=mNav"
print(addr)

column_names = ["Year", "name", "league", "playerId", "teamId", "abbrev", "keeperValue", "auctionValue",
                "keeperPremium", "playerPosition"]

entries = []
with urllib.request.urlopen(addr) as url:
    data = json.loads(url.read().decode())
    for j in data['teams']:
        team_id = int(j['id'])
        abbrev = str(j['abbrev'])
        roster_key = 'rosterForCurrentScoringPeriod'
        if roster_key not in j.keys():
            roster_key = 'roster'
        for k in j[roster_key]['entries']:
            espn_id = int(k['playerId'])
            keeper_value = int(k['playerPoolEntry']['keeperValue'])
            player_full_name = k['playerPoolEntry']['player']['fullName']
            player_position = int(k['playerPoolEntry']['player']['defaultPositionId'])
            auction_value = 0
            if 'draftRanksByRankType' in k['playerPoolEntry']['player'].keys():
                auction_value = k['playerPoolEntry']['player']['draftRanksByRankType']['STANDARD']['auctionValue']
            keeper_premium = int(auction_value) - int(keeper_value)
            entry = [year, player_full_name, league, espn_id, team_id, abbrev,
                     keeper_value, auction_value, keeper_premium, player_position]
            entries.append(entry)

df = pd.DataFrame(entries, columns=column_names)

table_name = "ESPNKeepers"
df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


# for index, row in df.iterrows():
#     print(index)
#     print(row)
