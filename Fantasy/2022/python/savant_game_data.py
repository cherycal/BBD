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
import random
import pandas as pd
import logging
from pathlib import Path
import colorlog
import os
from io import BytesIO
from os import path
import certifi
import pycurl

from slack_sdk import WebClient

slack_api_token = os.environ["SLACK_BOT_TOKEN"]
slack_channel = os.environ["SLACK_CHANNEL"]
slack_client = WebClient(token=slack_api_token)
slack_most_recent = ""
slack_first_run = True

script_name = os.path.basename(__file__)


def roster_list():
    global PLAYOFFS
    teams = dict()
    try:
        r = bdb.select_plus("SELECT * FROM ESPNRostersWithMLBID")
        for d in r['dicts']:
            mlbid = str(d["MLBID"])
            roster_spot = str(d["RosterSpot"])
            # PLAYOFFS = True
            if PLAYOFFS is False:
                if teams.get(mlbid):
                    teams[mlbid] += f'{roster_spot}  '
                else:
                    teams[mlbid] = f'{roster_spot}  '
    except Exception as ex:
        print(f'Exception: {str(ex)}')
    return teams


def get_logger(logfilename="./logs/" + script_name + '.log',
               logformat='%(asctime)s:%(levelname)s'
                         ':%(funcName)s:%(lineno)d:%(message)s:%(pathname)s\n'):
    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{logformat}'
    )
    colorlog.basicConfig(format=colorlog_format)

    logger_inst = logging.getLogger(__name__)

    formatter = logging.Formatter(logformat)
    file_handler = logging.FileHandler(logfilename)
    file_handler.setFormatter(formatter)
    logger_inst.addHandler(file_handler)

    return logger_inst


now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")

p = Path.cwd()
log_dir = p / 'logs'
log_dir.mkdir(mode=0o755, exist_ok=True)
log_file = log_dir / 'game_data.txt'
log_filename = str(log_file)
logger_instance = get_logger(logfilename="./logs/" + script_name + f'_{out_date}.log')
logger_instance.setLevel(logging.DEBUG)

# logging.basicConfig(filename=log_filename,
#                     level=logging.INFO,
#                     filemode='w',
#                     format='%(asctime)s :%(levelname)s :%(lineno)d :%(message)s')
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# logging.info("Hello, info")

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy(caller=script_name)

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
        " (select TeamName as Team from ESPNTeamOwners where WatchLevel > 0)"

PLAYOFFS = False

if PLAYOFFS is True:
    query = "select distinct MLBID, Name from ( select  round(MLBID,0) as MLBID, " \
            "Name, AuctionValueAverage from ESPNPlayerDataCurrent E, IDMap I where " \
            " E.espnid = I.ESPNID and MLBID is not NULL ) union select distinct round(MLBID,0) as MLBID, Name " \
            "from ESPNPlayerDataCurrent E, IDMap I where  E.espnid = I.ESPNID and MLBID is not NULL"

print(query)

query_result = bdb.select(query)

for row in query_result:
    watch_ids.append(str(int(row[0])))

gamepks = list()

c = bdb.select("select game from StatcastGameData where date = " + str(out_date))
for t in c:
    gamepks.append(str(t[0]))

sc_first_run = dict()

# if PLAYOFFS is True:
#     sc_first_run = False

mlb_first_run = 1
reported_event_count = dict()
reported_statcast_count = dict()
event_count: Dict[Any, Any] = dict()
statcast_count: Dict[Any, Any] = dict()
has_statcast = dict()
is_in_pitching_change = dict()


def read_slack():
    global slack_most_recent
    global slack_first_run
    history = slack_client.conversations_history(channel=slack_channel,
                                                 tokem=slack_api_token, limit=1)
    msgs = history['messages']
    text = ""
    if len(msgs) > 0:
        for msg in msgs:
            text = msg['text']
            if text != slack_most_recent:
                try:
                    slack_most_recent = text
                    if not slack_first_run:
                        break
                    else:
                        print(F"Skipping slack first run")
                        slack_first_run = False
                except Exception as ex:
                    inst.push(f"Error in push_instance, Error: {str(ex)}")
            else:
                pass
    return text


def process_mlb(data, gamepk, player_teams):
    global watch_ids
    global reported_event_count
    global event_count
    global PLAYOFFS
    global sc_first_run
    global is_in_pitching_change
    plays = data['liveData']['plays']['allPlays']
    # print("Game: " + str(gamepk))
    home_team = str(data['gameData']['teams']['away']['name']).split()[-1]
    if home_team == "Sox":
        home_team = ' '.join(data['gameData']['teams']['away']['name'].split()[-2:])
    away_team = str(data['gameData']['teams']['home']['name']).split()[-1]
    if away_team == "Sox":
        away_team = ' '.join(data['gameData']['teams']['home']['name'].split()[-2:])
    print(f'{away_team} vs {home_team} at {datetime.now().strftime("%Y%m%d-%H%M%S")}')
    # print("************ START PLAYS *****************")
    for play in plays:
        at_bat = 0
        if play.get('about') and play['about'].get('atBatIndex') >= 0:
            at_bat = play['about']['atBatIndex'] + 1
        event_count[gamepk] = at_bat
        if at_bat == 1:
            if play['about'].get('isComplete') and play['about']['isComplete']:
                player_teams = roster_list()
            else:
                continue
        if play['result'].get('eventType') and play['result']['eventType'] == "game_advisory":
            print(f'Game advisory {away_team} vs {home_team}')
            continue

        if play['result'].get('description'):
            description = str(play['result']['description'])
            description = description.replace(" a ", " ")
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
            description = description.replace("right field", "RF")
            description = description.replace("left field", "LF")
            description = description.replace("center field", "CF")
            description = description.replace("homers", "HRs")
            description = description.replace("swinging", "swg")
            description = description.replace("line drive", "liner")
            description = description.replace("grounds", "gds")
            description = description.replace(" sharply", "")
            description = description.replace("sharp", "")
            description = description.replace("double play", "DP")
            description = description.replace("sacrifice", "sac")
            description = description.replace(" softly", "")
            description = description.replace("hit by pitch", "HBP")
            description = description.replace("ild pitch", "P")
            description = description.replace("  ", " ")
            # print(f'At description {at_bat}, description: {description}')
        else:
            description = "None"
        # print(f'Event count: {event_count[gamepk]}, Reported event count {reported_event_count[gamepk]}, At bat {at_bat}')
        if event_count[gamepk] > reported_event_count[gamepk]:

            if play['result'].get('eventType') and play['result']['eventType'] == 'pitching_substitution':
                # print(f'In pitching change: {is_in_pitching_change}')
                # logger_instance.info(f'Full play info: {play} ')
                if is_in_pitching_change.get(gamepk) is True:
                    # print(f'Game is in pitching change. Do not report')
                    continue
                else:
                    # print(f'Setting in pitching change to True ( in substitution ): {is_in_pitching_change}')
                    is_in_pitching_change[gamepk] = True
                    # print(f'Post set pitching change: {is_in_pitching_change}')
            else:
                # print(f'Setting in pitching change to False ( not in substitution ): {is_in_pitching_change}')
                is_in_pitching_change[gamepk] = False
                # print(f'Post set pitching change: {is_in_pitching_change}')

            # logger_instance.info(f'Full play info: {play} ')
            on_base = list('---')
            logger_instance.info(f'Home team {home_team}, Away team {away_team} ')
            logger_instance.info(f'At bat {at_bat}, description: {description} ')
            batter_id = str(play['matchup']['batter']['id'])
            batter_name = str(play['matchup']['batter']['fullName'])
            pitcher_id = str(play['matchup']['pitcher']['id'])
            pitcher_name = str(play['matchup']['pitcher']['fullName'])
            if play['matchup'].get('postOnFirst'):
                on_base[2] = '1'
            if play['matchup'].get('postOnSecond'):
                on_base[1] = '2'
            if play['matchup'].get('postOnThird'):
                on_base[0] = '3'

            on_base_str = f'{on_base[0]}{on_base[1]}{on_base[2]}'

            batter_teams = player_teams.get(batter_id, "No teams") if PLAYOFFS is False else ""
            pitcher_teams = player_teams.get(pitcher_id, "No teams") if PLAYOFFS is False else ""

            print("At bat: " + str(at_bat))
            logger_instance.info(f'At bat {at_bat}, Batter: {batter_name}, Pitcher: {pitcher_name}')
            print("Batter: " + batter_name)
            print("Pitcher: " + pitcher_name)
            if batter_id in watch_ids or pitcher_id in watch_ids:
                # print(play)
                home_score = play['result']['awayScore']
                away_score = play['result']['homeScore']
                inning = str(play['about']['halfInning'])[0].capitalize() + "" + str(play['about']['inning'])
                outs = str(play['count']['outs'])
                # logger_instance.info(f'On watch list: {play}')
                # print("Batter ID: " + batter_id)
                # print("Pitcher ID: " + pitcher_id)
                if description != "None":
                    # logger_instance.info(f'Play info: {play}')
                    # print(f'\n\n{play}\n\n')
                    # print("event: " + str(event_count[gamepk]))
                    msg = f"\r\n*\r\n"
                    msg += f"{description[0:160]}"  # TWEET DESCRIPTION LENGTH
                    # logger_instance.info(f'Play description: {msg}')
                    msg += f'\nP: {pitcher_name} {pitcher_teams}\n{home_team} {home_score}, ' \
                           f'{away_team} {away_score}, {inning} {outs}o, {on_base_str}\n' \
                           f'{batter_teams}'
                    msg = msg[0:280]
                    # print("----------")
                    print(msg)
                    # print("-----------------------------------------------")
                    title = msg[0:140]
                    if not sc_first_run[gamepk] or at_bat <= 1:
                        logger_instance.info(f'Pushing play info: {msg}')
                        print("Pushing: " + msg)
                        inst.push(title, msg)
                        # inst.tweet(msg)
                        time.sleep(1.25)
                    else:
                        print("Not pushing on SC first run")
                        logging.info(f'Not pushing on first run')
                        time.sleep(1.25)
                else:
                    logger_instance.info(f'Not pushing new play with no description. At bat number {at_bat}')
            else:
                if description != "None":
                    print("Skipped play, players not on watch list: " +
                          str(event_count[gamepk]))
                    logger_instance.info(f'Players not on watch list: {description}')
                    # print(play)
                    # print("-----------------------------------------------")
            if play.get('about') and play['about'].get('isComplete'):
                isComplete = play['about']['isComplete']
                print(f'Completed at bat {at_bat}? {isComplete}')
                reported_event_count[gamepk] = at_bat
            else:
                print(f'At bat not complete, decrementing at bat reported_event_count to {at_bat - 1}')
                reported_event_count[gamepk] = at_bat - 1
        else:
            pass
            # print(f'Skipping reported event number {event_count[gamepk]}')
    sc_first_run[gamepk] = False
    # print("*********** END PLAYS ******************")


# NOT USED AS OF 20230506 #################
def process_statcast(data, gamepk):
    global watch_ids
    global reported_statcast_count
    global statcast_count
    global mlb_first_run
    global PLAYOFFS
    events = data['exit_velocity']
    for event in events:
        at_bat = 0
        if event.get('ab_number'):
            at_bat = event['ab_number']
        statcast_count[gamepk] = at_bat
        batter_id = str(event['batter'])
        pitcher_id = str(event['pitcher'])
        batter_name = event['batter_name']
        pitcher_name = event['pitcher_name']
        if statcast_count[gamepk] > reported_statcast_count[gamepk]:
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
                    msg2 = str(event['des'])[0:40]
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
                # print("--------------------")
                title = msg2[0:160] + " " + event['team_batting'] + " vs " + event['team_fielding']
                if not mlb_first_run:
                    inst.push(title, msg2)
                    # inst.tweet(msg2)
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
##################################################

def process_lineups(lineups):
    cols = ['date', 'gamepk', 'pitcher', 'batter', 'pitcher_team', 'batter_team', 'date8']
    lol = list()
    d = lineups['date']
    g = lineups['gamepk']
    a = lineups['at']
    h = lineups['ht']
    datetimeobject = datetime.strptime(d, '%m/%d/%Y')
    d8 = datetimeobject.strftime('%Y%m%d')
    for ap in lineups['ap']:
        for b in lineups['hb']:
            ll = [d, g, ap, b, a, h, d8]
            # print(ll)
            lol.append(ll)
    for hp in lineups['hp']:
        for b in lineups['ab']:
            ll = [d, g, hp, b, h, a, d8]
            # print(ll)
            lol.append(ll)

    table_name = "DailyLineups"
    delcmd = "delete from " + table_name + " where Date = '" + d + "' and gamepk = " + g
    # print(delcmd)
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


def get_savant_gamefeed_page(url_name):
    TIMEOUT = 10
    headers = ["authority: baseballsavant.mlb.com"
        ,
               "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        , "accept-language: en-US,en;q=0.9"
        , "cache-control: max-age=0"
        , "dnt: 1"
        , "if-modified-since: Sat, 08 Apr 2023 19:59:59 GMT"
        , "sec-ch-ua: \"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\""
        , "sec-ch-ua-mobile: ?0"
        , "sec-ch-ua-platform: \"Windows\""
        , "sec-fetch-dest: document"
        , "sec-fetch-mode: navigate"
        , "sec-fetch-site: none"
        , "sec-fetch-user: ?1"
        , "upgrade-insecure-requests: 1"
        ,
               "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
               ]

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url_name)
    c.setopt(c.CONNECTTIMEOUT, TIMEOUT)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()
    data = buffer.getvalue()
    return json.loads(data)


def start_gamefeed(gamepks):
    global has_statcast
    global reported_event_count
    global reported_statcast_count
    lineups = dict()
    TIMEOUT = 15
    SLEEP_BASE = 60

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

        sc_first_run[gamepk] = True

    not_eod = True
    # run_count = 0
    slack_on = True

    while not_eod:

        now = datetime.now()
        time6 = now.strftime("%H%M%S")
        print(f'Current time: {time6}')

        current_time = int(time6)
        if current_time > 225800:
            print(f'End of day exit')
            exit(0)

        not_eod = False
        games = len(gamepks)

        print(f'Games left: {games}: {gamepks}')

        if slack_on and read_slack() == "EGF":
            slack_on = False
            print(f"Slack flag is now set to OFF")

        if not slack_on:
            if read_slack() == "SGF":
                slack_on = True
                print(f"Slack flag is now set to ON")

        if slack_on:
            in_progress_games = 0
            for gamepk in gamepks:

                not_eod = True

                sleep_min = int(max(8,SLEEP_BASE / games))
                sleep_max = sleep_min + 14

                ts = datetime.now()  # current date and time
                # formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
                update_time = ts.strftime("%Y%m%d%H%M%S")

                try:
                    cmd = "update ProcessUpdateTimes set UpdateTime = {} where Process = 'GameData'".format(update_time)
                    # print(cmd)
                    bdb.update(cmd)
                except Exception as ex:
                    print(str(ex))
                    inst.push("DB error in savant_game_data", str(ex))
                    # inst.tweet("DB error in game_data: " + str(ex))

                ########### Statcast ######################

                url_name = "https://baseballsavant.mlb.com/gf?game_pk=" + gamepk
                print(url_name)

                try:
                    data = get_savant_gamefeed_page(url_name)
                    statcast_count[gamepk] = 0

                    if data.get('game_status_code'):
                        print(f"Game code for {gamepk}: {data['game_status_code']}")
                        if data['game_status_code'] == 'I':
                            in_progress_games += 1
                        if data['game_status_code'] == "F":
                            print(f'Skipping completed game: {gamepk}')
                            print("Sleep for 2 seconds ")
                            time.sleep(1)
                            if gamepks.count(gamepk):
                                gamepks.remove(gamepk)
                                logger_instance.info(f'Removing {gamepk} from list')
                            continue
                        else:
                            # print("Sleep at " + formatted_date_time)
                            sleep_seconds = random.randint(sleep_min, sleep_max)

                            if reported_event_count[gamepk] == 0:
                                sleep_seconds += 0

                            print(f"Sleep for {str(sleep_seconds)} seconds ( SLEEP_BASE is {SLEEP_BASE} )")
                            time.sleep(sleep_seconds)

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
                        print("Skipping statcast data")
                        # process_statcast(data, gamepk)
                except Exception as ex:
                    print(f'Exception in user code: {ex}')
                    print("-" * 60)
                    traceback.print_exc(file=sys.stdout)
                    print("-" * 60)
                    time.sleep(4)

                ############  MLB  ###################

                url_name = "http://statsapi.mlb.com/api/v1.1/game/" + gamepk + "/feed/live"
                # print(url_name)

                try:
                    with urllib.request.urlopen(url_name, timeout=TIMEOUT) as url2:
                        event_count[gamepk] = 0
                        data = json.loads(url2.read().decode())
                        if data.get('liveData'):
                            #SLEEP_BASE = 15
                            print(f'\nReporting MLB data for {gamepk}')
                            process_mlb(data, gamepk, player_teams)
                        else:
                            print("MLB data unavailable")
                except Exception as ex:
                    print(f'Exception in user code: {ex}')
                    print("-" * 60)
                    traceback.print_exc(file=sys.stdout)
                    print("-" * 60)
                    time.sleep(4)

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
            print(f"In progress games = {in_progress_games}")
            if in_progress_games == 0:
                SLEEP_BASE = 400
            else:
                SLEEP_BASE = 15

        else:
            loop_sleep = 15
            print(f"Slack flag set to OFF - sleeping for {loop_sleep} seconds")
            time.sleep(15)
            not_eod = True

    print("Games are done for today")
    try:
        bdb.update("update ProcessUpdateTimes set Active = 0 where Process = 'GameData'")
    except Exception as ex:
        print(str(ex))


def main():
    start_gamefeed(gamepks)


if __name__ == "__main__":
    main()
