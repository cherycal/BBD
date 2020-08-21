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
import inspect

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


#
#     fantasy.get_db_player_info()
#     fantasy.get_espn_player_info(populate_player_data_current_table)
#

def print_calling_function():
    print(str(inspect.stack()[-2].filename) + ", " + str(inspect.stack()[-2].function) +
          ", " + str(inspect.stack()[-2].lineno))
    print(str(inspect.stack()[1].filename) + ", " + str(inspect.stack()[1].function) +
          ", " + str(inspect.stack()[1].lineno))
    print(str(inspect.stack()[-1].filename) + ", " + str(inspect.stack()[-1].function) +
          ", " + str(inspect.stack()[-1].lineno))
    return


def begin_day_process():
    ts = datetime.now()  # current date and time
    out_time = ts.strftime("%Y%m%d-%H%M%S")
    print(out_time)

    fantasy.get_db_player_info()

    command = ""
    tries = 0
    TRIES_BEFORE_QUITTING = 3
    SLEEP = 5
    passed = 0
    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        try:
            command = "Delete from PlayerDataCurrent"
            bdb.delete(command)
            print("\nDelete PlayerDataCurrent worked\n")
            passed = 1
            break
        except Exception as ex:
            inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time), command + ": " + str(ex))
        time.sleep(SLEEP)

        if not passed:
            inst.push("DATABASE ERROR", command)

    insert_many_list = fantasy.get_espn_player_info()

    tries = 0
    passed = 0

    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        try:
            print(insert_many_list[0])
            bdb.insert_many("PlayerDataCurrent", insert_many_list)
            print("\ninsert PlayerDataCurrent worked\n")
            passed = 1
            break
        except Exception as ex:
            inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time),
                      "Insert PlayerDataCurrent" + ": " + str(ex))
        time.sleep(SLEEP)

    if not passed:
        inst.push("DATABASE ERROR", "insert PlayerDataCurrent, espn_player_info")
    else:
        inst.push("BEGIN DAY PROCESS SUCCEEDS", "insert PlayerDataCurrent, espn_player_info")


def eod_process():
    command = ""
    tries = 0
    passed = 0
    TRIES_BEFORE_QUITTING = 3
    SLEEP = 5
    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        try:
            command = "insert into PlayerDataHistory select * from PlayerDataCurrent"
            bdb.insert(command)
            passed = 1
            break
        except Exception as ex:
            inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time), command + ": " + str(ex))
        time.sleep(SLEEP)

    if not passed:
        inst.push("DATABASE ERROR: " + str(date_time), "espn_player_info.py")
    else:
        inst.push("EOD PROCESS SUCCEEDS: " + str(date_time), "espn_player_info.py")

    return


def run_function(function, name="none given"):
    print("\n")
    print(function)
    print(name)
    return


def main():

    while 1:
        ts = datetime.now()  # current date and time
        out_time = ts.strftime("%Y%m%d-%H%M%S")
        time8 = ts.strftime("%H%M%S")
        print("Start at " + out_time)

        if int(time8) < 200:
            fantasy.refresh_rosters_table()
        if int(time8) >= 235800:
            eod_process()
        if 40000 <= int(time8) < 40200:
            begin_day_process()

        run_function(fantasy.get_db_player_info(), 'get_db_player_info')
        run_function(fantasy.get_espn_player_info(), 'get_espn_player_info')
        run_function(fantasy.get_player_info_changes(), 'get_player_info_changes')
        run_function(fantasy.send_push_msg_list(), 'send_push_msg_list')
        run_function(fantasy.run_transactions(), 'run_transactions')

        print("Sleep at " + out_time)
        time.sleep(115)


if __name__ == "__main__":
    main()
