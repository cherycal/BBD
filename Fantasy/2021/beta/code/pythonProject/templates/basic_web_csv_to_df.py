import sys

import pandas as pd

sys.path.append('../modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

df = pd.read_csv("http://dailybaseballdata.com/cgi-bin/dailyhit.pl?date=&xyear=0&pa=1&showdfs=&sort=ops&r40=0&scsv=2&nohead=1")
print(df)

