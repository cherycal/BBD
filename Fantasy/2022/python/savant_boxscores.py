import json
import sys
import urllib.request

sys.path.append('./modules')
import sqldb
import time
import random
import push
import pandas as pd
import fantasy
from datetime import date, datetime
from datetime import timedelta
import os

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
mode = "PROD"
fantasy = fantasy.Fantasy(mode, caller=os.path.basename(__file__))


def process_statcast(data, gamepk, game_date):
    away_team = data['boxscore']['teams']['away']
    home_team = data['boxscore']['teams']['home']
    print("Game: " + str(gamepk))

    for team in [home_team, away_team]:
        batlol = list()
        pitchlol = list()
        batters = team['batters']
        pitchers = team['pitchers']
        column_names = ['name', 'team', 'date', 'points', 'totalBases', 'runs', 'rbi', 'stolenBases',
                        'baseOnBalls', 'strikeOuts', 'doubles', 'triples', 'homeRuns',
                        'hits', 'atBats', 'caughtStealing', 'hitByPitch',
                        'groundIntoDoublePlay', 'intentionalWalks', 'mlbid', 'gamepk']
        batcats = ['points', 'totalBases', 'runs', 'rbi', 'stolenBases',
                   'baseOnBalls', 'strikeOuts', 'doubles', 'triples', 'homeRuns',
                   'hits', 'atBats', 'caughtStealing', 'hitByPitch',
                   'groundIntoDoublePlay', 'intentionalWalks', 'gamepk', 'mlbid', 'name', 'team', 'date']
        index = list()
        teamname = team['team']['name'].split(" ")[-1]

        for batter in batters:
            statlist = list()
            bid = "ID" + str(batter)
            bname = team['players'][bid]['person']['fullName']
            game_stats = team['players'][bid]['stats']['batting']
            season = str(game_date)
            season = season[0:4]
            gametype = "R"
            for cat in batcats:
                if game_stats.get(cat):
                    statlist.append(game_stats[cat])
                else:
                    statlist.append(0)
            points = sum(statlist[1:6]) - statlist[6]
            statlist[-1] = game_date
            statlist[-2] = teamname
            statlist[-3] = bname
            statlist[-4] = bid[2:]
            statlist[-5] = gamepk
            statlist[0] = points
            batlol.append(statlist)
            index.append("")
            print(bid)
            print(bname)
            print(batcats)
            print(statlist)
            print("")

        df = pd.DataFrame(batlol, columns=batcats, index=index)
        print(df.columns)
        df = df.sort_values(by=['points'], ascending=[False])
        df = df[column_names]
        df['pa'] = df['atBats'] + df['baseOnBalls'] + df['hitByPitch']
        df['singles'] = df['hits'] - df['doubles'] - df['triples'] - df['homeRuns']
        df['wOBA'] = ((df['baseOnBalls'] + df['hitByPitch']) * .7 + df['singles'] * .9 + df['doubles'] * 1.25 + df[
            'triples'] * 1.6 + df['homeRuns'] * 2.0) / df['pa']
        df['wOBA'] = df['wOBA'].apply(lambda x: round(x, 4))
        df['OBP'] = (df['hits'] + df['baseOnBalls'] + df['hitByPitch']) / df['pa']
        df['OBP'] = df['OBP'].apply(lambda x: round(x, 4))
        df['SLG'] = (df['singles'] * 1.0 + df['doubles'] * 2.0 + df['triples'] * 3.0 + df['homeRuns'] * 4.0) / df[
            'atBats']
        df['SLG'] = df['SLG'].apply(lambda x: round(x, 4))
        df['GameType'] = "R"
        df['Season'] = season
        # df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
        img = "mytable.png"
        #dfi.export(df, img)
        #inst.tweet_media(img, "Batting stats: " + teamname)

        table_name = "StatcastBoxscores"
        del_cmd = f'delete from {table_name} where gamepk = {gamepk} and team = \'{teamname}\''
        not_passed = True
        while not_passed:
            try:
                print(del_cmd)
                bdb.delete(del_cmd)
                not_passed = False
            except Exception as ex:
                print("DB Error")
                inst.push("DATABASE ERROR at " + str(game_date),
                          del_cmd + ": " + str(ex))
                time.sleep(2)

        try:
            df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
        except Exception as ex:
            print(str(ex))

        column_names = ['name', 'team', 'date', 'points', 'qs', 'outs', 'strikeOuts', 'wins', 'saves', 'holds',
                        'earnedRuns', 'baseOnBalls', 'losses', 'hits', 'gamesStarted', 'intentionalWalks', 'mlbid',
                        'gamepk']

        pitchcats = ['points', 'qs', 'outs', 'strikeOuts', 'wins', 'saves', 'holds',
                     'earnedRuns', 'baseOnBalls', 'losses', 'hits', 'gamesStarted', 'intentionalWalks', 'gamepk',
                     'mlbid',
                     'name', 'team', 'date']

        index.clear()
        for pitcher in pitchers:
            pid = "ID" + str(pitcher)
            statlist = list()
            pname = team['players'][pid]['person']['fullName']
            game_stats = team['players'][pid]['stats']['pitching']
            print(pid)
            print(pname)
            print(game_stats)
            print("")
            qs = 0
            for cat in pitchcats:
                if game_stats.get(cat):
                    statlist.append(game_stats[cat])
                else:
                    statlist.append(0)
            if game_stats['outs'] >= 18 and game_stats['earnedRuns'] <= 3:
                qs = 1
            points = 2 * qs + game_stats['outs'] + game_stats['strikeOuts'] + \
                     game_stats['wins'] + \
                     5 * game_stats['saves'] + 3 * game_stats['holds'] - \
                     2 * game_stats['earnedRuns'] - \
                     game_stats['baseOnBalls'] - game_stats['losses'] - \
                     game_stats['hits']
            statlist[-1] = game_date
            statlist[-2] = teamname
            statlist[-3] = pname
            statlist[-4] = pid[2:]
            statlist[-5] = gamepk
            statlist[0] = points
            statlist[1] = qs
            pitchlol.append(statlist)
            print(pname)
            print(pitchcats)
            print(statlist)
            index.append("")

        df = pd.DataFrame(pitchlol, columns=pitchcats, index=index)
        print(df.columns)
        df = df.sort_values(by=['points'], ascending=[False])
        df = df[column_names]
        df['GameType'] = "R"
        df['Season'] = season
        # df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
        img = "mytable.png"
        #dfi.export(df, img)
        #inst.tweet_media(img, "Pitching stats: " + teamname)

        table_name = "StatcastBoxscoresPitching"
        del_cmd = f'delete from {table_name} where gamepk = {gamepk} and team = \'{teamname}\''
        print(del_cmd)
        bdb.delete(del_cmd)
        df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


def one_day(dt):
    now = datetime.now()  # current date and time
    out_date = now.strftime("%Y%m%d")

    override_date = dt

    if override_date != "":
        out_date = override_date

    gamepks = dict()

    q = f'select game, date from StatcastGameData where date >= {out_date} and date <= {out_date} ' \
        f'and (game_state = "Final" or game_state is NULL)'

    c = bdb.select(q)

    for t in c:
        gamepks[str(t[0])] = str(t[1])

    ts = datetime.now()  # current date and time
    formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
    for gamepk in gamepks:

        url_name = "https://baseballsavant.mlb.com/gf?game_pk=" + gamepk

        print(url_name)

        with urllib.request.urlopen(url_name) as url:

            data = json.loads(url.read().decode())

            if data.get('exit_velocity'):
                print("Reporting statcast data")
                process_statcast(data, gamepk, gamepks[gamepk])
            else:
                print("Statcast data unavailable, checking for MLB Data")
                url_name = "http://statsapi.mlb.com/api/v1.1/game/" + gamepk + "/feed/live"
                print(url_name)
                with urllib.request.urlopen(url_name) as url2:
                    data = json.loads(url2.read().decode())
                    if data.get('liveData'):
                        print("Skipping MLB data")
                        continue
                    # process_mlb(data, gamepk)
                    else:
                        print("MLB data unavailable")

        print("Sleep at " + formatted_date_time)
        num1 = random.randint(1, 1)
        print("Sleep for " + str(num1) + " seconds")
        time.sleep(num1)


def main():
    DAYS_AGO = 2
    end_date = date.today()
    start_date = end_date - timedelta(days=DAYS_AGO)
    step = timedelta(days=1)

    # date1 = '2022-03-18'
    # date2 = '2022-03-27'
    # start_date = datetime.strptime(date1, '%Y-%m-%d')
    # end_date = datetime.strptime(date2, '%Y-%m-%d')

    while start_date <= end_date:
        d = start_date.strftime("%Y%m%d")
        one_day(str(d))
        start_date += step


if __name__ == "__main__":
    main()
