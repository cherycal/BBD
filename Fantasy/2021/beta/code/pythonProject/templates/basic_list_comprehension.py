import sys
from datetime import datetime

sys.path.append('../modules')
import sqldb
import push
import fantasy
import os

script_name = os.path.basename(__file__)

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy(caller= script_name)

integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

watch_ids = list()
query = "select distinct MLBID, Name from ( select  round(MLBID,0) as MLBID, " \
    "Name,R.Team, AuctionValueAverage from ESPNPlayerDataCurrent E, IDMap I," \
    " ESPNRosters R  where E.espnid = R.ESPNID and  E.espnid = I.ESPNID " \
    "and AuctionValueAverage >= 50 ) union select distinct round(MLBID,0) as MLBID," \
    " Name from ESPNPlayerDataCurrent E, IDMap I, ESPNRosters R where" \
    " E.espnid = R.ESPNID and  E.espnid = I.ESPNID and R.Team in" \
    " ('When Franimals Attack' ,'Spring Rakers', 'Flip Mode', " \
    "'Called Shots','wOBA Barons','Avengers:  Age Of Beltran'," \
    "'Avengers: Age Of Beltran','The Big Bang Theory','Great Bambi','The Terminators')"

print(query)

query_result = bdb.select(query)

watch_ids = [str(int(row[0])) for row in query_result]

print(watch_ids)