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

def get_mins_into_day(time):
    return int(time[0:2]) * 60 + int(time[2:4])

fantasy.tweet_daily_schedule(msg="Today's schedule")

while 1:


    warning_time = 15

    curtime = fantasy.get_hhmmss()
    curdate = fantasy.get_date8()

    query = "select substr(GameTime,9,17) as Time " \
            "from ESPNGameData where Date = " + \
            str(curdate) + " and Time > '" + \
            str(curtime)  + "' order by Time limit 1"

    print(query)
    c = bdb.select(query)
    next_start = "000000"
    for t in c:
        print(t[0])
        next_start = t[0]

    curmins = get_mins_into_day(str(curtime))
    stmins = get_mins_into_day(next_start)

    time_to_next_start = int(stmins) - int(curmins)
    print(time_to_next_start)

    if time_to_next_start > 0 and time_to_next_start < warning_time:
        inst.push("Game about to Start")
        fantasy.tweet_daily_schedule(msg="Game about to start")
        fantasy.tweet_sprk_on_opponents()
        fantasy.tweet_fran_on_opponents()
        fantasy.tweet_oppo_rosters()
        time.sleep(warning_time*40)

    if time_to_next_start < 0:
        exit(0)

    time.sleep(240)

#
# df = pd.DataFrame(np.random.randn(6, 6), columns=list('ABCDEF'))
#
# df_styled = df.style.background_gradient() #adding a gradient based on values in cell
#
# dfi.export(df_styled,"mytable.png")
