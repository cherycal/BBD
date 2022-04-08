import json
import sys
import traceback
import urllib.request
from datetime import datetime
from typing import Dict, Any

sys.path.append('./modules')
import sqldb
import push
import fantasy
import time
import csv
from os import path
import random
import pandas as pd
import logging
from pathlib import Path
import colorlog
import os

script_name = os.path.basename(__file__)

def roster_list():
    global PLAYOFFS
    teams = dict()
    try:
        r = bdb.select_plus("SELECT * FROM ESPNRostersWithMLBID")
        for d in r['dicts']:
            #leagueID = int(str(d["LeagueID"])[0:2])
            mlbid = str(d["MLBID"])
            #team = d["Team"]
            #full_team = str(team) #make a copy
            #team = team.replace("The ","")
            #team = team[0:4]
            #pos = "-"+str(d["Position"])
            roster_spot = str(d["RosterSpot"])
            #PLAYOFFS = True
            if PLAYOFFS == False:
                # if team not in ["Pitc","Senz","Flip","When","wOBA","Prac"]:
                #     team = leagueID
                #     pos = ""
                if teams.get(mlbid):
                    teams[mlbid] += f'{roster_spot} '
                else:
                    teams[mlbid] = f'{roster_spot} '

    except Exception as ex:
        print(f'Exception: {str(ex)}')

    return teams


def get_logger(logfilename = "./logs/" + script_name + '.log',
               logformat = '%(asctime)s:%(levelname)s'
                           ':%(funcName)s:%(lineno)d:%(message)s:%(pathname)s\n'):

    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{logformat}'
    )
    colorlog.basicConfig(format=colorlog_format)

    logger_instance = logging.getLogger(__name__)
    logger_instance.setLevel(logging.DEBUG)

    formatter = logging.Formatter(logformat)
    file_handler = logging.FileHandler(logfilename)
    file_handler.setFormatter(formatter)
    logger_instance.addHandler(file_handler)

    return logger_instance


now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")

p = Path.cwd()
log_dir = p / 'logs'
log_dir.mkdir(mode=0o755, exist_ok=True)
log_file = log_dir / 'game_data.txt'
log_filename = str(log_file)
logger_instance = get_logger(logfilename = "./logs/" + script_name + f'_{out_date}.log')

# logging.basicConfig(filename=log_filename,
#                     level=logging.INFO,
#                     filemode='w',
#                     format='%(asctime)s :%(levelname)s :%(lineno)d :%(message)s')
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# logging.info("Hello, info")

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy(caller= script_name)


integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)


# logging.info(f'Game data for {out_date}')

watch_ids = list()
query = "select distinct MLBID, Name from ( select  round(MLBID,0) as MLBID, " \
    "Name,R.Team, AuctionValueAverage from ESPNPlayerDataCurrent E, IDMap I," \
    " ESPNRosters R  where E.espnid = R.ESPNID and  E.espnid = I.ESPNID " \
    "and AuctionValueAverage >= 50 ) union select distinct round(MLBID,0) as MLBID," \
    " Name from ESPNPlayerDataCurrent E, IDMap I, ESPNRosters R where" \
    " E.espnid = R.ESPNID and  E.espnid = I.ESPNID and R.Team in" \
    " ('When Franimals Attack' , 'Flip Mode', 'wOBA Barons', 'Senzeless Violence','Practice Squad','Pitchers .')"

PLAYOFFS = False

if PLAYOFFS == True:
    query = "select distinct MLBID, Name from ( select  round(MLBID,0) as MLBID, " \
            "Name, AuctionValueAverage from ESPNPlayerDataCurrent E, IDMap I where " \
            " E.espnid = I.ESPNID ) union select distinct round(MLBID,0) as MLBID, Name " \
            "from ESPNPlayerDataCurrent E, IDMap I where  E.espnid = I.ESPNID"

print(query)

query_result = bdb.select(query)

for row in query_result:
    watch_ids.append(str(int(row[0])))

gamepks = list()

c = bdb.select("select game from StatcastGameData where date = " + str(out_date))
for t in c:
    gamepks.append(str(t[0]))

sc_first_run = 1

if PLAYOFFS == True:
    sc_first_run = 0

mlb_first_run = 1
reported_event_count = dict()
reported_statcast_count = dict()
event_count: Dict[Any, Any] = dict()
statcast_count: Dict[Any, Any] = dict()
has_statcast = dict()
is_in_pitching_change = False

def process_mlb(data, gamepk, player_teams):
    global watch_ids
    global reported_event_count
    global event_count
    global PLAYOFFS
    global sc_first_run
    global is_in_pitching_change
    plays = data['liveData']['plays']['allPlays']
    #print("Game: " + str(gamepk))
    home_team = str(data['gameData']['teams']['away']['name']).split()[-1]
    away_team = str(data['gameData']['teams']['home']['name']).split()[-1]
    print(f'{away_team} vs {home_team} at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
    #print(away_team)
    # print(watch_ids)
    # print("MLB data: events " + str(len(plays)))
    #print("Previously reported events: " +
    #      str(reported_event_count[gamepk]))
    #print("************ START PLAYS *****************")
    for play in plays:
        # event_count[gamepk] += 1
        at_bat = 0
        if play.get('about') and play['about'].get('atBatIndex'):
            at_bat = play['about']['atBatIndex']
        event_count[gamepk] = at_bat
        if at_bat == 1:
            player_teams = roster_list()
        description = ""
        if at_bat == 0:
            continue
        if play['result'].get('eventType') and play['result']['eventType'] == "game_advisory":
            print(f'Game advisory {away_team} vs {home_team}')
            continue
        if play['result'].get('eventType') and play['result']['eventType'] == 'pitching_substitution':
            if is_in_pitching_change:
                continue
            else:
                is_in_pitching_change = True
            time.sleep(100)
        else:
            is_in_pitching_change = False
        if play['result'].get('description'):
            description = str(play['result']['description'])
            description = description.replace("first baseman", "1B")
            description = description.replace("second baseman", "2B")
            description = description.replace("third baseman", "3B")
            description = description.replace("left fielder", "LF")
            description = description.replace("center fielder", "CF")
            description = description.replace("right fielder", "RF")
            description = description.replace("shortstop", "SS")
            description = description.replace("catcher", "C")
            description = description.replace("pitcher", "P")
            description = description.replace("strikes out", "Ks")
            description = description.replace("called out on strikes", "Ks")
            description = description.replace("walks", "BBs")
            description = description.replace("singles", "sgls")
            description = description.replace("doubles", "dbls")
            description = description.replace("triples", "tpls")
            description = description.replace("homers", "HRs")
            description = description.replace("swinging", "swg")
            description = description.replace("line drive", "liner")
            description = description.replace("grounds", "gds")
            description = description.replace("sharply", "")
            description = description.replace("sharp", "")
            #print(f'At description {at_bat}, description: {description}')
        else:
            description = "None"
        #print(f'Event count: {event_count[gamepk]}, Reported event count {reported_event_count[gamepk]}, At bat {at_bat}')
        if event_count[gamepk] > reported_event_count[gamepk]:
            # logger_instance.info(f'Full play info: {play} ')
            logger_instance.info(f'Home team {home_team}, Away team {away_team} ')
            logger_instance.info(f'At bat {at_bat}, description: {description} ')
            batter_id = str(play['matchup']['batter']['id'])
            batter_name = str(play['matchup']['batter']['fullName'])
            pitcher_id = str(play['matchup']['pitcher']['id'])
            pitcher_name = str(play['matchup']['pitcher']['fullName'])

            batter_teams = player_teams.get(batter_id,"No teams") if PLAYOFFS == False else ""
            pitcher_teams = player_teams.get(pitcher_id,"No teams") if PLAYOFFS == False else ""

            print("At bat: " + str(at_bat))
            logger_instance.info(f'At bat {at_bat}, Batter: {batter_name}, Pitcher: {pitcher_name}')
            print("Batter: " + batter_name)
            print("Pitcher: " + pitcher_name)
            if batter_id in watch_ids or pitcher_id in watch_ids:
                print(play)
                home_score = play['result']['awayScore']
                away_score = play['result']['homeScore']
                inning = str(play['about']['halfInning']) + " " + str(play['about']['inning'])
                outs = str(play['count']['outs'])
                #logger_instance.info(f'On watch list: {play}')
                #print("Batter ID: " + batter_id)
                #print("Pitcher ID: " + pitcher_id)
                if description != "None":
                    #print("----------")
                    #print("event: " + str(event_count[gamepk]))
                    msg = description[0:110]
                    logger_instance.info(f'Play description: {msg}')
                    msg += "\nP: " + pitcher_name + \
                           f' {pitcher_teams}\n{home_team} {home_score}, ' \
                           f'{away_team} {away_score}, {inning} {outs} O, AB {at_bat}\n' \
                           f'{batter_teams}\n'
                    msg = msg[0:220]
                    #print("----------")
                    print(msg)
                    #print("-----------------------------------------------")
                    title = msg[0:40]
                    logger_instance.info(f'Pushing play info: {msg}')
                    print("Pushing: " + msg)
                    if not sc_first_run and at_bat > 1:
                        inst.push(title, msg)
                        inst.tweet(msg)
                        time.sleep(.25)
                    else:
                        print("Not pushing on SC first run")
                        logging.info(f'Not pushing on first run')
                        time.sleep(.25)
                else:
                    logger_instance.info(f'Not pushing new play with no description. At bat number {at_bat}')
            else:
                if description != "None":
                    print("Skipped play, players not on watch list: " +
                          str(event_count[gamepk]))
                    logger_instance.info(f'Players not on watch list: {description}')
                    print(play)
                    #print("-----------------------------------------------")
            if play.get('about') and play['about'].get('isComplete'):
                isComplete = play['about']['isComplete']
                print(f'Completed at bat {at_bat}? {isComplete}')
            else:
                at_bat -= 1
                print(f'Decrementing at bat reported_event_count to {at_bat}')
            reported_event_count[gamepk] = at_bat
    sc_first_run = 0
    #print("*********** END PLAYS ******************")


def process_statcast(data, gamepk):
    global watch_ids
    global reported_statcast_count
    global statcast_count
    global mlb_first_run
    global PLAYOFFS
    msg2 = ""
    events = data['exit_velocity']
    #print("Game: " + str(gamepk))
    #print(data['away_team_data']['name'])
    #print(data['home_team_data']['name'])
    # print(watch_ids)
    # print("Statcast events: " + str(len(events)))
    #print("Previously reported events: " +
        #  str(reported_statcast_count[gamepk]))
    for event in events:
        # statcast_count[gamepk] += 1
        at_bat = 0
        if event.get('ab_number'):
            at_bat = event['ab_number']
        statcast_count[gamepk] = at_bat
        batter_id = str(event['batter'])
        pitcher_id = str(event['pitcher'])
        batter_name = event['batter_name']
        pitcher_name = event['pitcher_name']
        if statcast_count[gamepk] > reported_statcast_count[gamepk]:
            #print("At bat number: " + str(at_bat))
            #print("Batter: " + batter_name)
            #print("Pitcher: " + pitcher_name)
            if batter_id in watch_ids or pitcher_id in watch_ids:
                time.sleep(1)
                msg = "-----------------------------------------------"
                msg += "\n" + "Gamepk: " + str(gamepk)
                msg += "\n" + "Savant data: event number " + str(statcast_count[gamepk])
                msg += "\n" + "Previously reported events: " + str(reported_statcast_count[gamepk])
                msg += "\n" + batter_name
                msg += ", " + event['team_batting']
                msg += "\n" + pitcher_name
                msg += ", " + event['team_fielding']
                if event.get('des'):
                    msg2 = str(event['des'])
                    msg2 += "\nPitcher: " + pitcher_name
                else:
                    msg2 = f'Batter: {batter_name}\nPitcher: {pitcher_name}'
                if event.get('result'):
                    msg += "\n" + event['result']
                if event.get('xba'):
                    msg2 += "\n" + "xba: {0}".format(str(event['xba']))
                if event.get('hit_distance'):
                    msg2 += "\n" + "hit distance: {0}".format(str(event['hit_distance']))
                if event.get('hit_speed'):
                    msg2 += "\n" + "hit speed: " + str(event['hit_speed'])
                if event.get('hit_angle'):
                    msg2 += "\n" + "hit angle: " + str(event['hit_angle']) + "\n"
                msg += "\n" + "-----------------------------------------------"
                print(msg)
                print("--------------------")
                print(msg2)
                print("--------------------")
                #print("--------------------")
                title = msg2[0:20] + " " + event['team_batting'] + " vs " + event['team_fielding']
                if not mlb_first_run:
                    inst.push(title, msg2)
                    inst.tweet(msg2)
                    time.sleep(.25)
                else:
                    print("Not pushing on MLB first run")
                    time.sleep(.5)
                reported_statcast_count[gamepk] = at_bat

            else:
                print("Skipped play, players not on watch list, play number " +
                      str(statcast_count[gamepk]))
                print(event)
                reported_statcast_count[gamepk] = at_bat

    mlb_first_run = 0


def process_lineups(lineups):
    cols = ['date', 'gamepk', 'pitcher', 'batter', 'pitcher_team', 'batter_team', 'date8']
    lol = list()
    d = lineups['date']
    g = lineups['gamepk']
    a = lineups['at']
    h = lineups['ht']
    datetimeobject = datetime.strptime(d, '%m/%d/%Y')
    d8 = datetimeobject.strftime('%Y%m%d')
    for p in lineups['ap']:
        for b in lineups['hb']:
            ll = [d, g, p, b, a, h, d8]
            # print(ll)
            lol.append(ll)
    for p in lineups['hp']:
        for b in lineups['ab']:
            ll = [d, g, p, b, h, a, d8]
            # print(ll)
            lol.append(ll)

    table_name = "DailyLineups"
    delcmd = "delete from " + table_name + " where Date = '" + d + "' and gamepk = " + g
    #print(delcmd)
    df = pd.DataFrame(lol, columns=cols)

    ## try
    try:
        bdb.delete(delcmd)
        df.to_sql(table_name, bdb.conn, if_exists='append',
                  index=False)
    except Exception as ex:
        time.sleep(5)
        print(str(ex))

    return


def main():
    global has_statcast
    global reported_event_count
    global reported_statcast_count
    lineups = dict()
    TIMEOUT = 10
    SLEEP_BASE = 25
    sleep_min = 8
    sleep_max = 10

    player_teams = roster_list()
    # for p in player_teams:
    #     print(f'{p}: {player_teams[p]}')

    try:
        bdb.update("update ProcessUpdateTimes set Active = 1 where Process = 'GameData'")
    except Exception as ex:
        print(str(ex))

    # Tells program how many events have been reported for each game
    # So that events aren't reported more than once
    if path.exists("event_count.csv"):
        with open('event_count.csv', mode='r') as inp:
            reader = csv.reader(inp)
            reported_event_count = {str(rows[0]): int(rows[1]) for rows in reader}

    # Sets counts to zero if event counts are not found in event_count.csv file
    if path.exists("statcast_count.csv"):
        with open('statcast_count.csv', mode='r') as inp2:
            reader2 = csv.reader(inp2)
            reported_statcast_count = {str(rows[0]): int(rows[1]) for rows in reader2}

    # Sets counts to zero if event counts are not found in event_count.csv file
    for gamepk in gamepks:
        if not event_count.get(gamepk):
            event_count[str(gamepk)] = 0
        if not reported_event_count.get(gamepk):
            reported_event_count[str(gamepk)] = 0

        if not statcast_count.get(gamepk):
            statcast_count[str(gamepk)] = 0
        if not reported_statcast_count.get(gamepk):
            reported_statcast_count[str(gamepk)] = 0

    not_eod = 1
    # run_count = 0

    while not_eod:

        not_eod = 0
        games = len(gamepks)

        for gamepk in gamepks:

            not_eod = 1
            sleep_min = int(SLEEP_BASE / games)
            sleep_max = sleep_min + 5

            ts = datetime.now()  # current date and time
            formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
            update_time = ts.strftime("%Y%m%d%H%M%S")

            try:
                cmd = "update ProcessUpdateTimes set UpdateTime = {} where Process = 'GameData'".format(update_time)
                #print(cmd)
                bdb.update(cmd)
            except Exception as ex:
                print(str(ex))
                inst.push("DB error in savant_game_data", str(ex))
                inst.tweet("DB error in game_data: " + str(ex))

            ########### Statcast ######################

            url_name = "https://baseballsavant.mlb.com/gf?game_pk=" + gamepk
            #print(url_name)

            try:
                with urllib.request.urlopen(url_name, timeout=TIMEOUT) as url:
                    statcast_count[gamepk] = 0
                    data = json.loads(url.read().decode())

                    if data.get('game_status_code'):
                        if data['game_status_code'] == "F":
                            print(f'Skipping completed game: {gamepk}')
                            print("Sleep for 2 seconds ")
                            time.sleep(2)
                            if gamepks.count(gamepk):
                                gamepks.remove(gamepk)
                                logger_instance.info(f'Removing {gamepk} from list')
                            continue
                        else:
                            #print("Sleep at " + formatted_date_time)
                            num1 = random.randint(sleep_min, sleep_max)
                            #print("Sleep for " + str(num1) + " seconds")
                            time.sleep(num1)

                    lineups['gamepk'] = gamepk
                    if not data.get('home_team_data'):
                        continue
                    if data.get('gameDate'):
                        lineups['date'] = data['gameDate']
                    lineups['ht'] = data['home_team_data']['abbreviation']
                    lineups['at'] = data['away_team_data']['abbreviation']
                    lineups['ab'] = data['away_lineup']
                    lineups['ap'] = data['away_pitcher_lineup']
                    lineups['hb'] = data['home_lineup']
                    lineups['hp'] = data['home_pitcher_lineup']
                    process_lineups(lineups)

                    if data.get('exit_velocity'):
                        #print("Skipping statcast data")
                        process_statcast(data, gamepk)
            except Exception as ex:
                print("Exception in user code:")
                print("-" * 60)
                traceback.print_exc(file=sys.stdout)
                print("-" * 60)

            ############  MLB  ###################

            url_name = "http://statsapi.mlb.com/api/v1.1/game/" + gamepk + "/feed/live"
            #print(url_name)

            try:
                with urllib.request.urlopen(url_name, timeout=TIMEOUT) as url2:
                    event_count[gamepk] = 0
                    data = json.loads(url2.read().decode())
                    if data.get('liveData'):
                        print(f'\nReporting MLB data for {gamepk}')
                        process_mlb(data, gamepk, player_teams)
                    else:
                        print("MLB data unavailable")
            except Exception as ex:
                print("Exception in user code:")
                print("-" * 60)
                traceback.print_exc(file=sys.stdout)
                print("-" * 60)

            # Record how many events have been reported to event_count.csv file
            with open('event_count.csv', 'w') as f:
                for key in reported_event_count.keys():
                    f.write("%s,%s\n" % (key, reported_event_count[key]))
            # f.close()

            with open('statcast_count.csv', 'w') as f:
                for key in reported_statcast_count.keys():
                    f.write("%s,%s\n" % (key, reported_statcast_count[key]))
            # f.close()

            # Records to the has_statcast.csv file from has_statcast dict
            with open('has_statcast.csv', 'w') as f:
                for key in has_statcast.keys():
                    f.write("%s,%s\n" % (key, 1 * has_statcast[key]))

        # f.close()

    print("Games are done for today")
    try:
        bdb.update("update ProcessUpdateTimes set Active = 0 where Process = 'GameData'")
    except Exception as ex:
        print(str(ex))


if __name__ == "__main__":
    main()
