__author__ = 'chance'

import json
import sys
import time
import urllib.request

import pandas as pd

sys.path.append('./modules')
import sqldb
import random

# My python class: sqldb.py
bdb = sqldb.DB('Baseball.db')


def get_team(teamid, unixtime, records, TeamName):
    MIN_SLEEP = 1
    MAX_SLEEP = 2
    SLEEP_INTERVAL = random.randint(MIN_SLEEP, MAX_SLEEP)
    addr = "https://cdn.fangraphs.com/api/depth-charts/roster?teamid=" + str(teamid) + "&loaddate=" + str(unixtime)
    # addr = "https://www.fangraphs.com/api/menu/menu-standings"
    print(addr)
    fields = ['teamid', 'player', 'playerid','oPlayerId',
              'position', 'mlbamid', 'age', 'bats', 'throws',
              'draftpick', 'roster40', 'season', 'proj_WAR', 'proj_bat_HR','mlevel',
              'proj_bat_SB', 'proj_PT',
              'proj_bat_OPS', 'PA', 'actual_bat_K%', 'actualz_bat_HR',
              'actualz_bat_SB', 'actualz_bat_OBP', 'actualz_bat_SLG',
              'actualz_bat_OPS', 'injurynotes', 'injurydate', 'loaddate']

    with urllib.request.urlopen(addr) as url:
        data = json.loads(url.read().decode())
        print(teamid)
        for line in data:
            # print(line)
            filtered_d = dict((k, line[k]) for k in fields if k in line)
            if filtered_d.get('playerid') or filtered_d.get('oPlayerId'):
                # print(filtered_d)
                if not filtered_d.get('playerid'):
                    filtered_d['playerid'] = filtered_d['oPlayerId']
                filtered_d['Team'] = TeamName[filtered_d['teamid']]
                del filtered_d['oPlayerId']
                records.append(filtered_d)
    time.sleep(SLEEP_INTERVAL)
    return records


def get_team_map():
    names, c = bdb.select_w_cols("SELECT * FROM FGTeamMap")
    TeamName = {}
    # names = list(map(lambda x: x[0], c.description))
    # print(names)
    for t in c:
        # print(t)
        TeamName[t[0]] = t[1]
    return TeamName


def main():
    TeamName = get_team_map()
    table_name = "FGCurrentUniverse"
    unixtime = str(int(time.time()))
    TEAMS = 30

    records = []
    for teamid in range(1, TEAMS + 1, 1):
        records = get_team(teamid, unixtime, records, TeamName)

    # print(records)
    df = pd.DataFrame.from_records(records)
    # print(df)

    if len(df):
        bdb.cmd("DELETE from " + table_name)
        df.to_sql(table_name, bdb.conn, if_exists='append', index=True)


if __name__ == "__main__":
    main()
