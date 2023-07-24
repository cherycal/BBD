__author__ = 'chance'

import sqldb

# My python class: sqldb.py

bdb = sqldb.DB('bdb.db')

c = bdb.select("SELECT * FROM Leagues")

for t in c:
    print(t[0])

bdb.close()
