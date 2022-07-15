import re
import sys
import time
from datetime import datetime
from operator import itemgetter

import unidecode

sys.path.append('./modules')
import push
import fantasy
import inspect
import random
import traceback
import pandas as pd
import pytz
from datetime import date, timedelta
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

mode = "PROD"

inst = push.Push()
fantasy = fantasy.Fantasy(mode, caller=os.path.basename(__file__))
bdb = fantasy.get_db()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
date8 = out_date
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

def trywrap(func):
    tries = 0
    max_tries = 4
    incomplete = True
    while incomplete and tries < max_tries:
        try:
            func()
            incomplete = False
        except Exception as ex:
            print(str(ex))
            tries += 1
            time.sleep(2.5)
            if tries == max_tries:
                print("Process failed: ")
                print("Exception in user code:")
                print("-" * 60)
                traceback.print_exc(file=sys.stdout)
                print("-" * 60)
                inst.push("Attempt failed:", f'Error: {ex}\nFunction: {func}')


def print_calling_function():
    print(str(inspect.stack()))
    print(str(inspect.stack()[-2].filename) + ", " + str(inspect.stack()[-2].function) +
          ", " + str(inspect.stack()[-2].lineno))
    print(str(inspect.stack()[1].filename) + ", " + str(inspect.stack()[1].function) +
          ", " + str(inspect.stack()[1].lineno))
    print(str(inspect.stack()[-1].filename) + ", " + str(inspect.stack()[-1].function) +
          ", " + str(inspect.stack()[-1].lineno))
    return


def process_oddsline(text):

    splittext = re.split("(SF)|(Giants)|"
                         "(SD)|(Padres)|"
                         "(HOU)|(Astros)|"
                         "(BAL)|(Orioles)|"
                         "(KC)|(Royals)|"
                         "(NY)|(Yankees)|"
                         "(Mets)|"
                         "(BOS)|(Red Sox)|"
                         "(TB)|(Rays)|"
                         "(TOR)|(Blue Jays)|"
                         "(ATL)|(Braves)|"
                         "(OAK)|(Athletics)|"
                         "(TEX)|(Rangers)|"
                         "(LA)|(Angels)|"
                         "(Dodgers)|"
                         "(OAK)|(Athletics)|"
                         "(SEA)|(Mariners)|"
                         "(COL)|(Rockies)|"
                         "(MIL)|(Brewers)|"
                         "(ARI)|(Diamondbacks)|"
                         "(MIN)|(Twins)|"
                         "(CHI)|(White Sox)|(Cubs)|"
                         "(PHI)|(Phillies)|"
                         "(PIT)|(Pirates)|"
                         "(WAS)|(Nationals)|"
                         "(BOS)|(Red Sox)|"
                         "(STL)|(Cardinals)|"
                         "(MIA)|(Marlins)|"
                         "(CLE)|(Indians)|"
                         "(CIN)|(Reds)|"
                         "(DET)|(Tigers)|"
                         " +|\xa0|(-\d+\.?\d+)|\+", text)
    # print(text)
    # print(splittext)
    res = [i for i in splittext if i]
    return res


def run_odds():
    utc_now = datetime.now(pytz.UTC)
    dt = date.today()
    odds_date8 = utc_now.strftime("%Y%m%d")
    odds_update_time = utc_now.strftime("%Y%m%d%H%M%S")

    url = "https://sportsbook.draftkings.com/leagues/baseball/2003?category=game-lines-&subcategory=game"
    dfs = pd.read_html(url)
    tbl = dfs[0]

    entries = []
    column_names = ["date", "name", "time", "Tm", "Team", "OU", "ML", "UpdateTime"]
    table_name = "Odds"

    count = 0
    for i in dfs:
        oddslines = i.iloc[:, 0:4]
        for oddsline in oddslines.values:
            oddslist = process_oddsline(' '.join(map(str, oddsline)))
            if len(oddslist) > 10:
                # print(oddslist)
                if any(char.isdigit() for char in oddslist[5]):
                    name = f'{oddslist[3]} {oddslist[4]}'
                else:
                    name = f'{oddslist[3]} {oddslist[4]} {oddslist[5]}'
                name = unidecode.unidecode(name)
                odds = list(itemgetter(0, 1, 2, -3, -1)(oddslist))
                odds.insert(0, name)
                odds.insert(0, odds_date8)
                odds.append(odds_update_time)
                if odds[4] == "Yankees":
                    odds[3] = "NYY"
                if odds[4] == "Mets":
                    odds[3] = "NYM"
                if odds[4] == "Angels":
                    odds[3] = "LAA"
                if odds[4] == "Dodgers":
                    odds[3] = "LAD"
                if odds[4] == "Cubs":
                    odds[3] = "CHC"
                if odds[4] == "White Sox":
                    odds[3] = "CHW"
                #print(f'{odds}')
                bdb.insert_list(table_name, odds, verbose=False)
                time.sleep(.5)
                entries.append(odds)
        if count == 0:
            dt = dt + timedelta(days=1)
            dt8 = dt.strftime("%Y%m%d")
        count += 1


def begin_day_process():
    ts = datetime.now()  # current date and time
    out_time = ts.strftime("%Y%m%d-%H%M%S")
    # print(out_time)

    fantasy.get_db_player_info()

    # command = ""
    # tries = 0
    TRIES_BEFORE_QUITTING = 3
    SLEEP = 1

    insert_many_list = fantasy.get_espn_player_info()

    tries = 0
    passed = False

    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        try:
            if len(insert_many_list) > 3000:
                command = "Delete from ESPNPlayerDataCurrent"
                bdb.delete(command)
                time.sleep(.5)
                bdb.insert_many("ESPNPlayerDataCurrent", insert_many_list)
                time.sleep(.5)
                passed = True
                break
            else:
                print("Skipping ESPNPlayerDataCurrent Refresh phase")
                time.sleep(2)
                passed = True
                break
        except Exception as ex:
            inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time),
                      "Insert ESPNPlayerDataCurrent" + ": " + str(ex))
            fantasy.logger_exception(f'begin_day_process ERROR:')

        time.sleep(SLEEP)

    if not passed:
        inst.push("DATABASE ERROR", "insert ESPNPlayerDataCurrent, "
                                    "espn_player_info")
    else:
        inst.push("BEGIN DAY PROCESS SUCCEEDS",
                  "insert ESPNPlayerDataCurrent, espn_player_info")


def eod_process():
    command = "delete from ESPNPlayerDataHistory where Date = '" + str(date8) + "'"
    try:
        bdb.delete(command)
    except Exception as ex:
        fantasy.logger_exception(f'DB error in cmd {command}: Exception: {ex}')

    tries = 0
    passed = 0
    TRIES_BEFORE_QUITTING = 3
    SLEEP = 2.5
    while tries < TRIES_BEFORE_QUITTING:
        tries += 1
        command = "insert into ESPNPlayerDataHistory select * from ESPNPlayerDataCurrent"
        try:
            bdb.insert(command)
            passed = 1
            break
        except Exception as ex:
            inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time), command + ": " + str(ex))
            fantasy.logger_exception(f'DB error in cmd {command}: Exception: {ex}')
        time.sleep(SLEEP)

    try:
        run_odds()
    except Exception as ex:
        print(ex)
    fantasy.refresh_starter_history()

    if not passed:
        inst.push("DB ERROR eod_process(): " + str(date_time), "espn_player_info.py")
    else:
        inst.push("EOD PROCESS SUCCEEDS: " + str(date_time), "espn_player_info.py")

    return


# noinspection PyUnusedLocal
def run_function(function, name="none given"):
    # print("Function: " + str(inspect.stack()[-2].code_context))
    return


def main():
    run_begin_day_process = True
    run_end_day_process = True
    run_roster_suite = True
    run_odds_bool = True
    begin_day_time = 10000
    end_day_time = 211500
    MIN_SLEEP = 45
    MAX_SLEEP = 65

    try:
        bdb.update("update ProcessUpdateTimes set Active = 1 where Process = 'PlayerInfo'")
    except Exception as ex:
        fantasy.logger_exception(f'update ProcessUpdateTimes ERROR')

    while True:
        ts = datetime.now()  # current date and time
        formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
        time6 = ts.strftime("%H%M%S")
        current_time = int(time6)
        minute = int(ts.strftime("%M"))
        if ( minute == 20 or minute == 0 ) and run_odds_bool:
            print("Running odds")
            try:
                run_odds()
            except Exception as ex:
                print(ex)
            run_odds_bool = False
        else:
            run_odds_bool = True

        print(f'Start at {formatted_date_time}')

        update_time = ts.strftime("%Y%m%d%H%M%S")

        cmd = ""
        try:
            cmd = "update ProcessUpdateTimes set UpdateTime = {} where Process = 'PlayerInfo'".format(update_time)
            bdb.update(cmd)
        except Exception as ex:
            print(str(ex))
            inst.push("DB error in player_info", str(ex))
            inst.tweet("DB error in player_info\n" + cmd + ":\n" + str(ex))
            # fantasy.post_log_msg(f'DB error in cmd {cmd}: Exception: {ex}')
            fantasy.logger_exception(f'DB error in cmd {cmd}: Exception: {ex}')

        if current_time >= end_day_time and run_end_day_process:
            # ESPNPlayerDataCurrent -> ESPNPlayerDataHistory
            fantasy.logger_instance.debug(f'Start eod_process at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
            eod_process()
            fantasy.logger_instance.debug(f'End eod_process at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
            run_end_day_process = False

        if current_time >= 221500:
            try:
                bdb.update("update ProcessUpdateTimes set Active = 0 where Process = 'PlayerInfo'")
            except Exception as ex:
                print(str(ex))
            break

        if begin_day_time <= current_time and run_begin_day_process:
            fantasy.logger_instance.debug(f'Start begin_day_process at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
            begin_day_process()
            fantasy.logger_instance.debug(f'End begin_day_process at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
            run_begin_day_process = False

        print(f'refresh_rosters at  {datetime.now().strftime("%Y%m%d-%H%M%S")}')
        fantasy.refresh_rosters()

        if run_roster_suite:
            fantasy.tweet_daily_schedule()
            fantasy.tweet_fran_on_opponents()
            fantasy.tweet_oppo_rosters()
            ##
            fantasy.refresh_statcast_schedule()
            fantasy.refresh_espn_schedule()
            fantasy.tweet_add_drops()
            fantasy.refresh_starter_history()
            try:
                run_odds()
            except Exception as ex:
                print(str(ex))
            run_roster_suite = False

        fantasy.check_roster_lock_time()

        # Retrieve baseline information from ESPNPlayerDataCurrent
        print(f'get_db_player_info at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
        fantasy.get_db_player_info()

        # ESPNPlayerDataCurrent, ESPNPlayerDataHistory, StatusChanges
        # Retrieve fron ESPN API
        print(f'get_espn_player_info at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
        fantasy.get_espn_player_info()

        # Check against ESPNPlayerDataCurrent table and make changes
        # Now done in get_espn_player_info: run_function(fantasy.get_player_info_changes())
        print(f'send_push_msg_list at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
        fantasy.send_push_msg_list()

        # Rosters and RosterChanges
        print(f'run_transactions at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
        fantasy.run_transactions()

        num1 = random.randint(MIN_SLEEP, MAX_SLEEP)

        # formatted_date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        print(f'Sleep at {datetime.now().strftime("%Y%m%d-%H%M%S")} for {num1} seconds')
        # fantasy.logger_instance.debug(f'Sleep at {datetime.now().strftime("%Y%m%d-%H%M%S")} for {num1} seconds')
        time.sleep(num1)

    exit(0)


if __name__ == "__main__":
    main()
