import sys

sys.path.append('./modules')
import sqldb
import push
from datetime import date, datetime
from datetime import timedelta

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
ts = datetime.now()  # current date and time

# date object from string
dt = datetime.strptime("20210513175614", "%Y%m%d%H%M%S")

diff = ts - dt
print(diff.total_seconds())


# format time as string
now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")

# timedelta
today = date.today()
yesterday = today - timedelta(days=1)
