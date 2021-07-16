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
	url_name = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

	print("url is: " + url_name)

	with urllib.request.urlopen(url_name) as url:
		data = json.loads(url.read().decode())
		print(type(data))

def main():
	get_page()
	driver.close()


if __name__ == "__main__":
	main()
