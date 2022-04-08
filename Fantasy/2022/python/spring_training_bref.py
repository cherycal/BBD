__author__ = 'chance'

import sys

sys.path.append('./modules')

import sqldb
from bs4 import BeautifulSoup as bs
import tools
import time
import re
import pandas as pd

# Push notifications off
# inst = push.Push()

sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")
# Database
bdb = sqldb.DB('Baseball.db')


def get_season(yr=2020, bp="batting"):
	str(yr + 1)
	yr = str(yr)
	print("Year: " + str(yr))
	print("Type: " + bp)

	csv_filename = "C:\\Users\\chery\\Documents\\BBD\\BREF\\" + bp \
	               + "\\" + str(yr) + "spring_training.csv"
	print("Filename is: " + csv_filename)

	f = open(csv_filename, "w")

	# https://www.baseball-reference.com/leagues/MLB/2020-spring-training-batting.shtml
	url = "https://www.baseball-reference.com/leagues/MLB/" + str(yr) + \
	      "-spring-training-" + bp + ".shtml"
	print("url is: " + url)

	driver.get(url)
	time.sleep(sleep_interval)
	html = driver.page_source
	soup = bs(html, "html.parser")
	tbl_id = "players_spring_" + bp

	results = soup.find_all('table', id=tbl_id)

	hdr = dict()
	hdr['batting'] = "LastName,FirstName,Age,Tm,OppQual,GS,G,PA,AB,R,H,2B,3B,HR," \
	                 "RBI,SB,CS,BB,SO,BA,OBP,SLG,OPS,TB,GDP,HBP,SH,SF,IBB,POS,Year,MLBID\n"
	hdr['pitching'] = "LastName,FirstName,Age,Tm,OppQual,GS,W,L,W-L%,ERA,G,GS,GF,CG,SHO,SV," \
	                  "IP,H,R,ER,HR,BB,IBB,SO,HBP,BK,WP,BF,WHIP,H9,HR9,BB9,SO9,SO/W,Year,MLBID\n"

	f.write(hdr[bp])

	for table in results:
		line = ""
		for tr in table.select('tr'):
			""
			playerid = 0
			so_w = "0"
			for td in tr.find_all('td'):
				if td.get('data-append-csv'):
					# tid = td['data-append-csv']
					playerinfo = td['data-append-csv'].split('=')
					playerid = playerinfo[2]
				if td.get('data-stat') and td['data-stat'] == 'pos_summary':
					continue
				value = td.get_text()
				if td.get('data-stat') and td['data-stat'] == 'team_ID':
					value = td.get_text()[0:3]
					value = value.replace(',', '')
				if td.get('data-stat') and td['data-stat'] == 'strikeouts_per_base_on_balls':
					if td.get_text() != '':
						so_w = td.get_text()
					value = so_w
				# value = td.get_text()
				value = value.replace('#', '')
				value = value.replace('*', '')
				value = value.replace('\t ', '')
				value = re.sub(r"\s+", '', value)
				# print(value)
				line += value + ","
			if len(line):
				# trim line, write to csv file
				line = line[:-2]
				line += "," + yr
				line += "," + playerid
				line += '\n'
				f.write(line)
				print(line)
				line = ""

	f.close()

	table_name = "SpringTraining" + bp.capitalize()

	del_cmd = "delete from " + table_name + " where Year = " + str(int(yr))
	bdb.delete(del_cmd)

	df = pd.read_csv(csv_filename)
	df.to_sql(table_name, bdb.conn, if_exists='append', index=False)



def main():
	for yr in [2021]:
		for bp in ["batting","pitching"]:
			get_season(yr, bp)
	driver.close()


if __name__ == "__main__":
	main()
