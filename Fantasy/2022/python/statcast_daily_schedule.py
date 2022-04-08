__author__ = 'chance'
import json
import sys
import time
import urllib.request
from datetime import date, datetime

sys.path.append('./modules')
import sqldb
import push
import fantasy
import tools
import pandas as pd

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time

# datetime.datetime.now() + datetime.timedelta(days=1) TOMORROW

date_time = now.strftime("%Y%m%d%H%M%S")
date8 = now.strftime("%Y%m%d")
statcast_date = now.strftime("%Y-%m-%d")

sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")

msg = ""

def get_page(date=statcast_date):

	date10 = str(date.strftime("%Y-%m-%d"))
	date8 = str(date.strftime("%Y%m%d"))
	url_name = "http://statsapi.mlb.com/api/v1/schedule?sportId=1,&date=" + date10

	print("url is: " + url_name)
	entries = []
	column_names = ['date','game','game_state']
	with urllib.request.urlopen(url_name) as url:
		data = json.loads(url.read().decode())
		for gamedate in data['dates']:
			for game in gamedate['games']:
				game_state = game['status'].get('detailedState','')
				print(date8 + "," + str(game['gamePk']))
				entry = [date8,game['gamePk'],game_state]
				entries.append(entry)

	df = pd.DataFrame(entries, columns=column_names)

	table_name = "StatcastGameData"
	delcmd = "delete from " + table_name + " where date = " + date8
	print(delcmd)
	bdb.delete(delcmd)
	df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
	time.sleep(sleep_interval)


def main():
	print("Range of dates")
	start_date = date(2022, 4, 1)
	end_date = date(2022, 10, 3)
	[get_page(date.fromordinal(i)) for i in range(start_date.toordinal(), end_date.toordinal())]
	driver.close()


if __name__ == "__main__":
	main()
