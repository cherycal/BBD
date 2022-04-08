__author__ = 'chance'
import sys
sys.path.append('../modules')
import sqldb

# My python class: sqldb.py

mode = "TEST"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')

#c = bdb.select("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ESPNPlayerDataCurrent'")
names,c = bdb.select_w_cols("SELECT * FROM ESPNLeagues")

#names = list(map(lambda x: x[0], c.description))
print(names)
for t in c:
    print(t)

bdb.close()
