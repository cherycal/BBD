import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta

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

print(fantasy.get_roster_lock_time())