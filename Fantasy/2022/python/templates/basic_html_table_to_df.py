import sys

import pandas as pd

sys.path.append('../modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2021&batSide=&stat=index_wOBA&condition=All&rolling=no"
dfs = pd.read_html(url)

print(dfs[0])
