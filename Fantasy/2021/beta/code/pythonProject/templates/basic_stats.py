__author__ = 'chance'
import sys
import time

import dataframe_image as dfi
import pandas as pd

sys.path.append('../modules')
import sqldb
import push

# My python class: sqldb.py
push_instance = push.Push()
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')
# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')

q = f'select Name, Season,G, PA, HR, R, RBI, "K%", AVG, OBP,' \
    f' SLG, wOBA from FGBattingCOmplete where Season in (1965,1966)'
r = bdb.select_plus(q)

count = 0
for row in r['rows']:
    count += 1
    lol = []
    lol.append(row)
    msg = f'{row[0]}: {int(row[1])}\n'
    print(f'{count}: {msg}')
    df = pd.DataFrame(lol, columns=r['column_names'], index=[""])
    img = "mytable.png"
    dfi.export(df, img)
    push_instance.tweet_media(img, msg)
    time.sleep(45)

bdb.close()

