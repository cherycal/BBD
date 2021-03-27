import json
import sys
import urllib.request
from datetime import datetime

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

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

watch_ids = list()
q = "select distinct MLBID from ( select  round(MLBID,0) as MLBID, Name," \
    "R.Team, AuctionValueAverage from ESPNPlayerDataCurrent E," \
               " IDMap I, ESPNRosters R where E.espnid = R.ESPNID and " \
               " E.espnid = I.ESPNID and AuctionValueAverage > 2 union " \
               "select  round(MLBID,0) as MLBID, Name, R.Team, AuctionValueAverage from " \
               "ESPNPlayerDataCurrent E, IDMap I, ESPNRosters R where " \
               "E.espnid = R.ESPNID and  E.espnid = I.ESPNID and " \
               "R.Team in ('When Franimals Attack' ,'SpringRakers' ))"

c = bdb.select(q)

for t in c:
    watch_ids.append(str(int(t[0])))

gamepks = list()

c = bdb.select("select game from StatcastGameData where date = " + str(out_date))
for t in c:
    gamepks.append(str(t[0]))

reported_event_count = dict()
event_count = dict()
has_statcast = dict()


def process_mlb(data, gamepk):
    global watch_ids
    global reported_event_count
    global event_count
    plays = data['liveData']['plays']['allPlays']
    print("Game: " + str(gamepk))
    #print(watch_ids)
    print("MLB data: events " + str(len(plays)))
    print("Previously reported events: " +
          str(reported_event_count[gamepk]))
    for play in plays:
        event_count[gamepk] += 1
        if event_count[gamepk] > reported_event_count[gamepk]:
            batter_id = str(play['matchup']['batter']['id'])
            batter_name = str(play['matchup']['batter']['fullName'])
            pitcher_id = str(play['matchup']['pitcher']['id'])
            pitcher_name = str(play['matchup']['pitcher']['fullName'])
            print(batter_name)
            print(pitcher_name)
            if batter_id in watch_ids or pitcher_id in watch_ids:
                print(play)
                print("Batter: " + batter_id)
                print("Pitcher: " + pitcher_id)
                if play['result'].get('description'):
                    print("-----------------------------------------------")
                    print("event: " + str(event_count[gamepk]))
                    msg = play['result']['description']
                    msg += "\nPitcher: " + pitcher_name
                    print("-----------------------------------------------")
                    print(msg)
                    print("-----------------------------------------------")
                    title = msg[0:40]
                    print("Pushing: " + msg)
                    inst.push(title, msg)
                    inst.tweet(msg)
                    reported_event_count[gamepk] += 1
                else:
                    print("Play has no description")
            else:
                print("-----------------------------------------------")
                print("Skipped play, players not on watch list: " +
                      str(event_count[gamepk]))
                print(play)
                print("-----------------------------------------------")
                reported_event_count[gamepk] += 1


def process_statcast(data, gamepk):
    global watch_ids
    global reported_event_count
    global event_count
    msg2 = ""
    events = data['exit_velocity']
    print("Game: " + str(gamepk))
    # print(watch_ids)
    print("Statcast events: " + str(len(events)))
    print("Previously reported events: " +
          str(reported_event_count[gamepk]))
    for event in events:
        event_count[gamepk] += 1
        batter_id = str(event['batter'])
        pitcher_id = str(event['pitcher'])
        batter_name = event['batter_name']
        pitcher_name = event['pitcher_name']
        if event_count[gamepk] > reported_event_count[gamepk]:
            print(batter_name)
            print(pitcher_name)
            if batter_id in watch_ids or pitcher_id in watch_ids:
                msg = "-----------------------------------------------"
                msg += "\n" + "Gamepk: " + str(gamepk)
                msg += "\n" + "Savant data: event number " + str(event_count[gamepk])
                msg += "\n" + "Previously reported events: " + str(reported_event_count[gamepk])
                msg += "\n" + event['batter_name']
                msg += ", " + event['team_batting']
                msg += "\n" + event['pitcher_name']
                msg += ", " + event['team_fielding']
                if event.get('des'):
                    msg2 = event['des']
                    msg2 += "\nPitcher: " + event['pitcher_name']
                if event.get('result'):
                    msg += "\n" + event['result']
                if event.get('xba'):
                    msg2 += "\n" + "xba: {0}".format(str(event['xba']))
                if event.get('hit_distance'):
                    msg2 += "\n" + "hit distance: {0}".format(str(event['hit_distance']))
                if event.get('hit_speed'):
                    msg2 += "\n" + "hit speed: " + str(event['hit_speed'])
                if event.get('hit_angle'):
                    msg2 += "\n" + "hit angle: " + str(event['hit_angle'])
                msg += "\n" + "-----------------------------------------------"
                print(msg)
                print("--------------------")
                print(msg2)
                print("--------------------")
                print("--------------------")
                title = msg2[0:20] + " " + event['team_batting'] + " vs " + event[
                    'team_fielding']
                inst.push(title, msg2)
                inst.tweet(msg2)
                reported_event_count[gamepk] += 1
            else:
                print("Skipped play, players not on watch list, play number " +
                      str(event_count[gamepk]))
                print(event)
                reported_event_count[gamepk] += 1


def main():

    global has_statcast
    global reported_event_count

    # Tells program how many events have been reported for each game
    # So that events aren't reported more than once
    if path.exists("event_count.csv"):
        with open('event_count.csv', mode='r') as inp:
            reader = csv.reader(inp)
            reported_event_count = {str(rows[0]): int(rows[1]) for rows in reader}

    # Sets counts to zero if event counts are not found in event_count.csv file
    for gamepk in gamepks:
        if not event_count.get(gamepk):
            event_count[str(gamepk)] = 0
        if not reported_event_count.get(gamepk):
            reported_event_count[str(gamepk)] = 0
            # print(gamepk)
            # print(reported_event_count[gamepk])

    # for i in reported_event_count:
    #     print(i)
    #     print(reported_event_count[i])

    while 1:
        ts = datetime.now()  # current date and time
        formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
        for gamepk in gamepks:

            url_name = "https://baseballsavant.mlb.com/gf?game_pk=" + gamepk

            print(url_name)

            with urllib.request.urlopen(url_name) as url:
                event_count[gamepk] = 0
                data = json.loads(url.read().decode())

                if data.get('exit_velocity'):
                    print("Reporting statcast data")
                    process_statcast(data, gamepk)
                else:
                    print("Statcast data unavailable, checking for MLB Data")
                    url_name = "http://statsapi.mlb.com/api/v1.1/game/" + gamepk + "/feed/live"
                    print(url_name)
                    with urllib.request.urlopen(url_name) as url2:
                        event_count[gamepk] = 0
                        data = json.loads(url2.read().decode())
                        if data.get('liveData'):
                            print("Reporting MLB data")
                            process_mlb(data, gamepk)
                        else:
                            print("MLB data unavailable")




            # Record how many events have been reported to event_count.csv file
            with open('event_count.csv', 'w') as f:
                for key in reported_event_count.keys():
                    f.write("%s,%s\n" % (key, reported_event_count[key]))
            f.close()

            # Records to the has_statcast.csv file from has_statcast dict
            with open('has_statcast.csv', 'w') as f:
                for key in has_statcast.keys():
                    f.write("%s,%s\n" % (key, 1 * has_statcast[key]))
            f.close()

            print("Sleep at " + formatted_date_time)
            num1 = random.randint(8, 18)
            print("Sleep for " + str(num1) + " seconds")
            time.sleep(num1)


if __name__ == "__main__":
    main()
