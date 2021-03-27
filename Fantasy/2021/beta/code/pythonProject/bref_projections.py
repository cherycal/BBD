__author__ = 'chance'

import sys

sys.path.append('./modules')

import sqldb
import requests
from bs4 import BeautifulSoup as bs
import tools
import time
import push
import pandas as pd

# Push notifications off
# inst = push.Push()

sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")
# Database
bdb = sqldb.DB('Baseball.db')


def get_season(yr=2017, bp="Batting", update_db=False):
	proj_yr = str(yr + 1)
	yr = str(yr)
	print("Year: " + str(yr))
	print("Type: " + bp)

	csv_filename = "C:\\Users\\chery\\Documents\\BBD\\BREF\\" + bp + "\\" + str(yr) + "projection.csv"
	print("Filename is: " + csv_filename)

	f = open(csv_filename, "w")

	url = "https://www.baseball-reference.com/leagues/MLB/" + str(yr) + "-projections.shtml"
	print("url is: " + url)

	driver.get(url)
	time.sleep(sleep_interval)
	html = driver.page_source
	soup = bs(html, "html.parser")

	if bp[0] == "B":
		results = soup.find_all('table', id="marcel_batting")
	elif bp[0] == "P":
		results = soup.find_all('table', id="marcel_pitching")
	else:
		print("Type not chosen - using batting as default")
		results = soup.find_all('table', id="marcel_batting")

	for table in results:
		line = ""
		for th in table.select('th'):
			if th.has_attr('class'):
				if 'poptip' in th['class']:
					if th.get_text() != "Rk":
						line += th.get_text() + ","
					if th.get_text() == "Rel":
						break
		if len(line):
			# trim line, write to csv file
			line = line[:-1]
			line += ",Year,id,PTS,1B"
			line += '\n'
			f.write(line)
			print(line)
			line = ""
		for tr in table.select('tr'):
			tid = ""
			for td in tr.find_all('td'):
				if td.get('data-append-csv'):
					tid = td['data-append-csv']
				line += td.get_text() + ","
			if len(line):
				# trim line, write to csv file
				line = line[:-2]
				line += "," + proj_yr
				line += "," + tid
				line += '\n'
				f.write(line)
				print(line)
				line = ""

	f.close()
	table_name = "BrefProjections_" + bp
	df = pd.read_csv(csv_filename, encoding="ISO-8859-1")

	if update_db:
		df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

	if bp == "Batting":

		#altercmd = "ALTER TABLE " + table_name + " ADD COLUMN \"1B\" INTEGER"
		#bdb.cmd(altercmd)

		updatecmd = "update " + table_name + " set \"1B\" = H-\"2B\"-\"3B\"-HR"
		bdb.update(updatecmd)

		updatecmd = "update " + table_name + " set PTS = R+RBI+SB+BB-SO+\"1B\"+2*\"2B\"+3*\"3B\"+4*HR"
		bdb.update(updatecmd)

	if bp == "Pitching":
		pass


	print("Year " + yr + " " + bp + " completed")


def main():
	for yr in [2020,2017,2018,2019]:
		for bp in ["Batting"]:
			get_season(yr, bp, update_db=False)
	driver.close()


if __name__ == "__main__":
	main()
