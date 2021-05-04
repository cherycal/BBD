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

df = pd.read_csv("http://dailybaseballdata.com/cgi-bin/dailyhit.pl?date=&xyear=0&pa=1&showdfs=&sort=ops&r40=0&scsv=2&nohead=1")
print(df)

