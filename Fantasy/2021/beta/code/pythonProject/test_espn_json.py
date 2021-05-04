__author__ = 'chance'

from bs4 import BeautifulSoup
import time
import json
import os
import sys
import time
import urllib.request


addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/87301?" \
       "view=mScoreboard&scoringPeriodId=161"
print(addr)

with urllib.request.urlopen(addr) as url:
    data = json.loads(url.read().decode())
    j = data

