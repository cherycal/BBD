import sys
import time
from datetime import datetime

sys.path.append('./modules')
import push
import fantasy
import inspect
import random

mode = "PROD"

inst = push.Push()
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)


def print_calling_function():
    print(str(inspect.stack()))
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

    #command = ""
    #tries = 0
    TRIES_BEFORE_QUITTING = 3
    SLEEP = 5


    insert_many_list = fantasy.get_espn_player_info()
    #run_function(fantasy.get_player_info_changes())

    tries = 0
    passed = 0

    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        try:
            print("First row of insert many list:")
            print(insert_many_list[0])
            print("Length of insert many list:")
            print(len(insert_many_list))
            if len(insert_many_list) > 3000:
                command = "Delete from ESPNPlayerDataCurrent"
                bdb.delete(command)
                print("\nDelete ESPNPlayerDataCurrent worked\n")
                bdb.insert_many("ESPNPlayerDataCurrent", insert_many_list)
                print("\ninsert ESPNPlayerDataCurrent worked\n")
                time.sleep(5)
                passed = 1
                break
            else:
                print("Skipping ESPNPlayerDataCurrent Refresh phase")
                time.sleep(5)
                passed = 1
                break
        except Exception as ex:
            inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time),
                      "Insert ESPNPlayerDataCurrent" + ": " + str(ex))
        time.sleep(SLEEP)

    if not passed:
        inst.push("DATABASE ERROR", "insert ESPNPlayerDataCurrent, espn_player_info")
    else:
        inst.push("BEGIN DAY PROCESS SUCCEEDS", "insert ESPNPlayerDataCurrent, espn_player_info")


def eod_process():
    command = ""
    tries = 0
    passed = 0
    TRIES_BEFORE_QUITTING = 3
    SLEEP = 5
    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        try:
            command = "insert into ESPNPlayerDataHistory select * from ESPNPlayerDataCurrent"
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


# noinspection PyUnusedLocal
def run_function(function, name="none given"):
    print("Function: " + str(inspect.stack()[-2].code_context))
    return


def main():
    run_begin_day_process = 1
    run_end_day_process = 1
    begin_day_time = 40000
    end_day_time = 211500

    while 1:
        ts = datetime.now()  # current date and time
        formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
        time6 = ts.strftime("%H%M%S")
        current_time = int(time6)
        print("Start at " + formatted_date_time)

        if current_time >= end_day_time and run_end_day_process:
            # ESPNPlayerDataCurrent -> ESPNPlayerDataHistory
            eod_process()
            run_end_day_process = 0

        if current_time >= 235500:
            exit(0)

        if begin_day_time <= current_time and run_begin_day_process:
            begin_day_process()
            run_begin_day_process = 0

        run_function(fantasy.refresh_rosters())

        # Retrieve baseline information from ESPNPlayerDataCurrent
        run_function(fantasy.get_db_player_info())

        # ESPNPlayerDataCurrent, ESPNPlayerDataHistory, StatusChanges
        # Retrieve fron ESPN API
        run_function(fantasy.get_espn_player_info())

        # Check against ESPNPlayerDataCurrent table and make changes
        # Now done in get_espn_player_info: run_function(fantasy.get_player_info_changes())

        run_function(fantasy.send_push_msg_list())

        # Rosters and RosterChanges
        run_function(fantasy.run_transactions())

        print("Sleep at " + formatted_date_time)
        num1 = random.randint(45, 85)
        print("Sleep for " + str(num1) + " seconds")
        time.sleep(num1)


if __name__ == "__main__":
    main()
