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
from datetime import date, datetime
from datetime import timedelta

inst = push.Push()
bdb = sqldb.DB('Baseball.db')

now = datetime.now()

t = now.strftime("%H:%M:%S")
print("time:", t)

today = date.today()

yesterday = today - timedelta(days=1)

stdt = date(2021,3,31)

print((yesterday-stdt).days)

print("Current year:", today.year)
print("Current month:", today.month)
print("Current day:", today.day)

print("yesterday year:", yesterday.year)
print("yesterday month:", yesterday.month)
print("yesterday day:", yesterday)


# convert date formats ...
d = "04/01/2021"
datetimeobject = datetime.strptime(d, '%m/%d/%Y')
d8 = datetimeobject.strftime('%Y%m%d')

## SQLITE date range using offsets ( no hardcoding )
c = bdb.select("select game from StatcastGameData where "
               "date >= strftime('%Y%m%d','now','-4 days') "
               "and date <= strftime('%Y%m%d','now')")
