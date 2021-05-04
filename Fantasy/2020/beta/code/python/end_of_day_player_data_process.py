import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

def main():
    command = ""
    tries = 0
    TRIES_BEFORE_QUITTING = 3
    SLEEP = 5
    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        try:
            command = "insert into ESPNPlayerDataHistory select * from ESPNPlayerDataCurrent"
            bdb.insert(command)
            exit(0)
        except Exception as ex:
            inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time), command + ": " + str(ex))
        time.sleep(SLEEP)

    inst.push("DATABASE ERROR: " + str(date_time), "end_of_day_player_data_process.py")


    exit()

if __name__ == "__main__":
    main()
