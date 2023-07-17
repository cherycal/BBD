__author__ = 'chance'

import json
import sys
import time
# noinspection PyCompatibility
import urllib.request
from datetime import datetime, date

sys.path.append('./modules')
import sqldb
import push
import fantasy
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


def get_page(statcast_date):
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


def main():
    start_date = date(2023, 7, 14)
    end_date = date(2023, 10, 3)
    [get_page(str(date.fromordinal(i))) for i in range(start_date.toordinal(), end_date.toordinal())]
    time.sleep(.5)


if __name__ == "__main__":
    main()
