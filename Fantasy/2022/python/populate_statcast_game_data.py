__author__ = 'chance'

## Populates StatcastGameData table with Games and Game Data from MLB

import json
import sys
import time
# noinspection PyCompatibility
import urllib.request
from datetime import datetime

import requests

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
# date8 = now.strftime("%Y%m%d")
# statcast_date = now.strftime("%Y-%m-%d")

sleep_interval = 1

msg = ""


def populate_one_day(statcast_date):
    date8 = str(statcast_date.replace("-", ""))
    url_name = f"http://statsapi.mlb.com/api/v1/schedule?sportId=1&date={statcast_date}"

    print("url is: " + url_name)
    entries = []
    column_names = ['date', 'game']
    with urllib.request.urlopen(url_name) as url:
        data = json.loads(url.read().decode())
        for gamedate in data['dates']:
            for game in gamedate['games']:
                print(date8 + "," + str(game['gamePk']))
                entry = [date8, game['gamePk']]
                entries.append(entry)

    df = pd.DataFrame(entries, columns=column_names)

    table_name = "StatcastGameData"
    delcmd = "delete from " + table_name + " where date = " + date8
    print(delcmd)
    bdb.delete(delcmd)
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
    time.sleep(.5)

def get_savant_gamefeed_page(url_name):
    #TIMEOUT = 10
    headers = {"authority": "baseballsavant.mlb.com"}
    #print("sleeping ....")
    time.sleep(.5)

    r = requests.get(url_name, headers=headers, allow_redirects=True)
    return json.loads(r.content)

def get_gamepks_from_db(start, end):
    return_list = list()
    try:
        r = bdb.select_plus(f"SELECT game FROM StatcastGameData where date >= {start} and date <= {end}")
        for d in r['rows']:
            return_list.append(d[0])
    except Exception as ex:
        print(f'Exception: {str(ex)}')
    return return_list

def update_games(gamelist):
    [update_game_data(gamepk) for gamepk in gamelist]

def update_game_data(gamepk):
    url_name = f"https://baseballsavant.mlb.com/gf?game_pk={str(gamepk)}"
    print(f"\n\nGame link: {url_name}")

    try:
        data = get_savant_gamefeed_page(url_name)
        time.sleep(.5)
        if data.get('scoreboard'):
            if data['scoreboard'].get('datetime'):
                if data['scoreboard']['datetime'].get('dateTime'):
                    game_time = data['scoreboard']['datetime']['dateTime']
                    local_game_time = tools.local_hhmmss_from_mlb_format(game_time)
                    print(f"Local game time: {local_game_time}")
                    table_name = "StatcastGameData"
                    updcmd = f"UPDATE {table_name} set start_time = {local_game_time} where game = {gamepk}"
                    print(updcmd)
                    bdb.cmd(updcmd)
    except Exception as ex:
        print(f"Error in update_game_data(): {ex}")

def get_start_times(game_date):
    return_dict = dict()
    try:
        r = bdb.select_plus(f"SELECT game,start_time FROM StatcastGameData where date = {game_date}")
        for d in r['dicts']:
            return_dict[d['game']] = d['start_time']
    except Exception as ex:
        print(f'Exception: {str(ex)}')
    return return_dict


def main():
    #start_date = date(2023, 7, 14)
    #end_date = date(2023, 10, 3)
    # If games aren't in the table yet for a given day, populate_one_day does it
    # It only enters a row for each game ( the game id is known as a gamepk )
    #[populate_one_day(str(date.fromordinal(i))) for i in range(start_date.toordinal(), end_date.toordinal())]
    #time.sleep(.5)
    #update_game_data(716910)
    #gamedates = get_gamepks_from_db("20230822","20231002")
    update_games(get_gamepks_from_db("20230822","20230822"))
    #print(get_start_times("20230822"))



if __name__ == "__main__":
    main()
