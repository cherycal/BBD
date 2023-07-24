__author__ = 'chance'

import json
import time
from datetime import datetime

import pytz
from pytz import timezone

eastern_tz = timezone('US/Eastern')
pacific_tz = timezone('US/Pacific')
fmt = '%Y-%m-%d %H:%M:%S %Z%z'

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(pacific_tz)
    return local_dt

class Activity(object):

    message_body: str

    def __init__(self):
          filename = 'file_text.json'
          url = 'http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/162788' \
                '?view=recentActivity'
          f = open(filename, 'r')
          text = f.read()
          text = text.replace('\n', '')
          array = json.loads(text)
          f.close()

          unix_ts = array["communication"]["topics"][1000]["date"] / 1000
          unix_dt = datetime.fromtimestamp(unix_ts)
          now_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
          current_dt = datetime.utcnow()

          print("Last activity: " + str(utc_to_local(unix_dt).strftime('%Y-%m-%d %H:%M:%S.%f '
                                                                       '%Z%z')))

          print("Now: " + str(utc_to_local(current_dt).strftime('%Y-%m-%d %H:%M:%S.%f '
                                                                       '%Z%z')))

          diff_dt = current_dt - unix_dt
          diff_hrs = diff_dt.days * 24 + diff_dt.seconds / 3600.0
          print("Hrs since last: " + str(diff_hrs))
          #print(array["communication"]["topics"][0]["date"])





#page = urllib.request.urlopen(url)
#html_content = page.read()
#rendered_content = html2text.html2text(str(html_content, encoding = "utf-8"))
#file = open(filename, 'w')
#file.write(rendered_content)
#file.close()
#print("File done")

