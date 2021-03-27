import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools, fantasy
import pickle
import os.path
from os import path
import push
import random

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
date_time2 = now.strftime("%Y%m%d-%H%M%S")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

teams = fantasy.active_leagues
while 1:
    fantasy.run_transactions(teams)
    num1 = random.randint(100, 125)
    now = datetime.now()  # current date and time
    date_time2 = now.strftime("%Y%m%d-%H%M%S")
    print(str(date_time2) + " " + str(num1))
    time.sleep(num1)
