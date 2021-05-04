import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path
import push
import fantasy
import inspect
import traceback
import random
import operator
import pycurl
import certifi
import io
from io import BytesIO


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

insert_many_list = fantasy.get_espn_player_info()
print("Entries in Player Data Current list:")
print(len(insert_many_list))
for i in insert_many_list:
    print(i)

# url = 'https://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/6455?view=kona_player_info'
# headers = ['authority: fantasy.espn.com',
#            'accept: application/json',
#            'x-fantasy-source: kona',
#            'x-fantasy-filter: {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS","ONTEAM"]},'
#            '"filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]}}}']
#
# buffer = BytesIO()
# c = pycurl.Curl()
# c.setopt(c.URL, url)
# c.setopt(c.HTTPHEADER, headers)
# c.setopt(c.WRITEDATA, buffer)
# c.setopt(c.CAINFO, certifi.where())
# c.perform()
# c.close()
#
# data  = buffer.getvalue()
#
# json_object = json.loads(data)
# json_formatted = json.dumps(json_object, indent=2)
#
# print(json_formatted)
