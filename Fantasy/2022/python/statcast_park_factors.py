__author__ = 'chance'

import sys

sys.path.append('./modules')

from bs4 import BeautifulSoup as bs
import tools
import time
import pandas as pd
import sqldb
from datetime import datetime

# My python class: sqldb.py

bdb = sqldb.DB('Baseball.db')

sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")

msg = ""


def get_page():
	now = datetime.now()  # current date and time
	# date_time = now.strftime("%Y%m%d%H%M%S")
	out_date = now.strftime("%Y%m%d")
	url = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?" \
	      "type=year&year=2021&batSide=&stat=index_wOBA&condition=All&rolling=no"
	print("url is: " + url)

	driver.get(url)
	time.sleep(sleep_interval)
	html = driver.page_source
	soup = bs(html, "html.parser")
	results = soup.find_all('div', {"id": ["parkFactors"]})

	entries = []
	headers = []
	for i in results:
		ths = i.find_all('th')
		headers = [th.text for th in ths]
		headers.append("update_date")
		print(headers)
		trs = i.find_all('tr')
		for tr in trs:
			tds = tr.find_all('td')
			if len(tds) > 1:
				row = [td.text for td in tds]
				row.append(out_date)
				if row[0] != "Rk.":
					print(row)
					entries.append(row)

	df = pd.DataFrame(entries, columns=headers)

	table_name = "StatcastParkFactors"
	df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


def main():
	get_page()
	driver.close()
	bdb.close()


if __name__ == "__main__":
	main()
