__author__ = 'chance'
import sys
sys.path.append('./modules')
import sqldb

# My python class: sqldb.py

bdb = sqldb.DB('Baseball.db')

#bdb = sqldb.DB('C:\\Ubuntu\\Shared\\data\\Baseball.db')

c = bdb.select("SELECT * FROM Leagues")

for t in c:
    print(t)

bdb.close()
