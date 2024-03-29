__author__ = 'chance'
import json
import sys
from datetime import datetime
sys.path.append('../modules')
import sqldb
import push
import fantasy
from io import BytesIO
import certifi
import pycurl

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
date8 = now.strftime("%Y%m%d")
statcast_date = now.strftime("%Y-%m-%d")

sleep_interval = 1

msg = ""


TIMEOUT = 10


def get_savant_gamefeed_page(url_name):

	headers = ["authority: baseballsavant.mlb.com"
			  ,  "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
	        ]

	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url_name)
	c.setopt(c.CONNECTTIMEOUT, TIMEOUT)
	c.setopt(c.HTTPHEADER, headers)
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.CAINFO, certifi.where())
	c.perform()
	c.close()
	data = buffer.getvalue()
	return json.loads(data)


def main():
	url = "https://baseballsavant.mlb.com/gf?game_pk=718666"
	data = get_savant_gamefeed_page(url)
	print(data)
	#driver.close()


if __name__ == "__main__":
	main()
