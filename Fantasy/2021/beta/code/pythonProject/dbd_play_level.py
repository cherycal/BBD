import pandas as pd
import numpy as np
import dataframe_image as dfi
import sys
sys.path.append('./modules')
import sqldb
import push
import fantasy
import time
import csv
from os import path
import random

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()
dt8 = fantasy.get_date8()

dt_override = ""
if dt_override != "":
	dt8 = dt8[0:6] + dt_override

df = pd.read_csv("http://rotoguru1.com/cgi-bin/mlb-dbd-2021.pl",sep=':')

df.insert(0, "Date", str(dt8) , True)
print(df)

# column_names = df.columns
# table_name = "DailyMatchups"
#
# delcmd = "DELETE from " + table_name + " where date = " + str(dt8)
# bdb.delete(delcmd)
# df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
