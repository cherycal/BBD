import sys

sys.path.append('../modules')
import sqldb
import push
import datetime
from datetime import date, timedelta
import pytz
import time

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
ts = datetime.datetime.now()  # current date and time

mlbtimestr = "2023-08-21T22:40:00Z"
mlbunixtime = datetime.datetime.strptime(mlbtimestr, "%Y-%m-%dT%H:%M:%SZ")
mlbunixtimestamp = mlbunixtime.timestamp()

nowtime = int(datetime.datetime.now().timestamp())
tzoffset = 3600 * (int(datetime.datetime.now(pytz.timezone('America/Tijuana')).strftime("%z")) / -100)

mlbdiff = (mlbunixtimestamp - (nowtime + tzoffset))/60

print(f'now utc {nowtime}')
print(f'str time {mlbunixtime}')
print(f'diff: {mlbdiff}')
exit(0)

print("unix time:" + str(int(time.time())))

# date object from string
dt = datetime.strptime("20210513175614", "%Y%m%d%H%M%S")

diff = ts - dt
print(diff.total_seconds())

# format time as string
now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")

# timedelta
DAYS_AGO = 5
print("Time delta:")
today = date.today()
yesterday = today - timedelta(days=1)
start_date = today - timedelta(days=DAYS_AGO)

# print(f'Today: {today.strftime("%Y%m%d")}')
# print(f'Yesterday: {yesterday.strftime("%Y%m%d")}')
# range of dates
print("Range of dates:")
date1 = '2023-07-14'
date2 = '2023-10-03'
start = datetime.strptime(date1, '%Y-%m-%d')
end = datetime.strptime(date2, '%Y-%m-%d')
step = timedelta(days=1)
while start <= end:
    print(start_date.strftime("%Y-%m-%d"))
    start += step

# range of dates
print("Range of dates")
start_date = date(2023, 7, 14)
end_date = date(2023, 10, 3)
[print(date.fromordinal(i)) for i in range(start_date.toordinal(), end_date.toordinal())]
