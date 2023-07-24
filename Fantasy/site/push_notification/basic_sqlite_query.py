__author__ = 'chance'

import sqldb

# My python class: sqldb.py

bdb = sqldb.DB('bdb.db')
#bdb = sqldb.DB('C:\\Ubuntu\\Shared\\first\\site\\data\\bdb.db')

c = bdb.select("SELECT * FROM Leagues")

for t in c:
    print(t)

bdb.close()
