__author__ = 'chance'

## Populates StatcastGameData table with Games and Game Data from MLB

import json
import sys
import time
# noinspection PyCompatibility
import urllib.request
from datetime import datetime, timedelta

sys.path.append('./modules')
import sqldb
import push
import fantasy
import tools
import pandas as pd

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")


def refresh_statcast_schedule(statcast_date):
    table_date = int(statcast_date.replace("-", ""))
    url_name = f"http://statsapi.mlb.com/api/v1/schedule?sportId=1,&date={statcast_date}"
    print("url is: " + url_name)
    entries = []
    column_names = ['date', 'game', 'game_state', 'start_time', 'play_count',
                    'home_team', 'home_team_id', 'away_team', 'away_team_id']
    with urllib.request.urlopen(url_name) as url:
        data = json.loads(url.read().decode())
        for gamedate in data['dates']:
            for game in gamedate['games']:
                # print(game)
                time.sleep(.5)
                local_game_time = tools.local_hhmmss_from_mlb_format(game['gameDate'])
                status = game['status']['statusCode']
                home_team = game['teams']['home']['team']['name']
                home_team_id = game['teams']['home']['team']['id']
                away_team = game['teams']['away']['team']['name']
                away_team_id = game['teams']['away']['team']['id']
                entry = [table_date, game['gamePk'], status, local_game_time, None,
                         home_team, home_team_id, away_team, away_team_id]
                # print(entry)
                entries.append(entry)

    df = pd.DataFrame(entries, columns=column_names)
    print(df)
    table_name = "StatcastGameData"
    delcmd = f"delete from {table_name} where date = {table_date}"
    bdb.delete(delcmd)
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


def main():
    date1 = '2023-09-18'
    date2 = '2023-10-03'
    start_date = datetime.strptime(date1, '%Y-%m-%d')
    end_date = datetime.strptime(date2, '%Y-%m-%d')
    step = timedelta(days=1)
    while start_date <= end_date:
        print(start_date.strftime("%Y-%m-%d"))
        refresh_statcast_schedule(start_date.strftime("%Y-%m-%d"))  # %Y-%m-%d
        start_date += step


if __name__ == "__main__":
    main()
