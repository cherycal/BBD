__author__ = 'chance'

import json
import sys
import time
import urllib.request

import pandas as pd

sys.path.append('./modules')
import sqldb
import random
import tools
from datetime import datetime

# My python class: sqldb.py
bdb = sqldb.DB('Baseball.db')


def get_fg_team_members(teamid, unixtime, records, TeamName, date8):
    MIN_SLEEP = 1
    MAX_SLEEP = 2
    SLEEP_INTERVAL = random.randint(MIN_SLEEP, MAX_SLEEP)
    addr = "https://cdn.fangraphs.com/api/depth-charts/roster?teamid=" + str(teamid) + "&loaddate=" + str(unixtime)
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
                filtered_d['loaddate8'] = date8
                del filtered_d['oPlayerId']
                records.append(filtered_d)
    time.sleep(SLEEP_INTERVAL)
    return records


def get_team_map():
    names, c = bdb.select_w_cols("SELECT * FROM FGTeamMap")
    TeamName = {}
    for t in c:
        TeamName[t[0]] = t[1]
    return TeamName


def process_fangraphs_universe():
    ts = datetime.now()  # current date and time
    formatted_date8 = ts.strftime("%Y%m%d")
    TeamName = get_team_map()
    table_name = "FGCurrentUniverse"
    unixtime = str(int(time.time()))
    TEAMS = 30

    records = []
    for teamid in range(1, TEAMS + 1, 1):
        records = get_fg_team_members(teamid, unixtime, records, TeamName, formatted_date8)

    df = pd.DataFrame.from_records(records)

    if len(df):
        #bdb.cmd("DELETE from " + table_name)
        df.to_sql(table_name, bdb.conn, if_exists='replace', index=True)

@tools.try_wrap
def main():
    process_fangraphs_universe()


if __name__ == "__main__":
    main()
