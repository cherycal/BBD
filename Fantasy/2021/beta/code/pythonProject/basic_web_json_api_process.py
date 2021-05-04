__author__ = 'chance'
import json
import sys
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb
import push
import fantasy
import tools

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
date8 = now.strftime("%Y%m%d")
statcast_date = now.strftime("%Y-%m-%d")

sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")

msg = ""

def get_page():
	url_name = "http://statsapi.mlb.com/api/v1/schedule?sportId=1,&date=" + statcast_date

	print("url is: " + url_name)

	with urllib.request.urlopen(url_name) as url:
		data = json.loads(url.read().decode())


def main():
	get_page()
	driver.close()


if __name__ == "__main__":
	main()
