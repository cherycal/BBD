import sys

sys.path.append('../modules')
import sqldb
import push
from datetime import date, datetime
from datetime import timedelta
import time
#import datetime

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
ts = datetime.now()  # current date and time

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
#range of dates
print("Range of dates:")
#date1 = '2021-03-31'
#date2 = '2021-05-12'
#start = datetime.strptime(start_date, '%Y-%m-%d')
#end = datetime.strptime(today, '%Y-%m-%d')
step = timedelta(days=1)
while start_date <= today:
    print(start_date.strftime("%Y%m%d"))
    start_date += step




#range of dates
print("Range of dates")
start_date = date(2022, 3, 22)
end_date = date(2022, 10, 6)
[print(date.fromordinal(i)) for i in range(start_date.toordinal(), end_date.toordinal())]
