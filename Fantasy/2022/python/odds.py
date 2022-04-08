import re
import sys
import time
from datetime import datetime

import pandas as pd

sys.path.append('./modules')
import sqldb
import push
import fantasy
from operator import itemgetter
import unidecode
import pytz
from datetime import date, timedelta
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
	ssl._create_default_https_context = ssl._create_unverified_context

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()


def process_oddsline(text):

	splittext = re.split('(SF)|(Giants)|'
	                     '(SD)|(Padres)|'
	                     '(HOU)|(Astros)|'
	                     '(BAL)|(Orioles)|'
	                     '(KC)|(Royals)|'
	                     '(NY)|(Yankees)|'
	                     '(Mets)|'
	                     '(BOS)|(Red Sox)|'
	                     '(TB)|(Rays)|'
	                     '(TOR)|(Blue Jays)|'
	                     '(ATL)|(Braves)|'
	                     '(OAK)|(Athletics)|'
	                     '(TEX)|(Rangers)|'
	                     '(LA)|(Angels)|'
	                     '(Dodgers)|'
	                     '(OAK)|(Athletics)|'
	                     '(SEA)|(Mariners)|'
	                     '(COL)|(Rockies)|'
	                     '(MIL)|(Brewers)|'
	                     '(ARI)|(Diamondbacks)|'
	                     '(MIN)|(Twins)|'
	                     '(CHI)|(White Sox)|(Cubs)|'
	                     '(PHI)|(Phillies)|'
	                     '(PIT)|(Pirates)|'
	                     '(WAS)|(Nationals)|'
	                     '(BOS)|(Red Sox)|'
	                     '(STL)|(Cardinals)|'
	                     '(MIA)|(Marlins)|'
	                     '(CLE)|(Indians)|'
	                     '(CIN)|(Reds)|'
	                     '(DET)|(Tigers)|'
	                     ' +|\xa0|(-\d+\.?\d+)|\+', text)

	res = [i for i in splittext if i]
	return res


def run_odds():
	utc_now = datetime.now(pytz.UTC)
	dt = date.today()
	dt8 = dt.strftime("%Y%m%d")

	odds_date8 = utc_now.strftime("%Y%m%d")
	odds_update_time = utc_now.strftime("%Y%m%d%H%M%S")

	url = "https://sportsbook.draftkings.com/leagues/baseball/2003?category=game-lines-&subcategory=game"
	dfs = pd.read_html(url)
	tbl = dfs[0]

	entries = []
	column_names = ["date", "name", "time", "Tm", "Team", "OU", "ML", "UpdateTime"]
	table_name = "Odds"

	count = 0
	for i in dfs:
		print(f'dt: {dt8}, i: {i}')
		oddslines = i.iloc[:, 0:4]
		for oddsline in oddslines.values:
			oddslist = process_oddsline(' '.join(map(str, oddsline)))
			#print(oddslist)
			if len(oddslist) > 10:
				#print(f'oddslist: {oddslist}')
				if any(char.isdigit() for char in oddslist[5]):
					name = f'{oddslist[3]} {oddslist[4]}'
				else:
					name = f'{oddslist[3]} {oddslist[4]} {oddslist[5]}'
				name = unidecode.unidecode(name)
				odds = list(itemgetter(0, 1, 2, -3, -1)(oddslist))
				odds.insert(0, name)
				odds.insert(0, dt8)
				odds.append(odds_update_time)
				if odds[4] == "Yankees":
					odds[3] = "NYY"
				if odds[4] == "Mets":
					odds[3] = "NYM"
				if odds[4] == "Angels":
					odds[3] = "LAA"
				if odds[4] == "Dodgers":
					odds[3] = "LAD"
				if odds[4] == "Cubs":
					odds[3] = "CHC"
				if odds[4] == "White Sox":
					odds[3] = "CHW"
				#print(f'{odds}')
				bdb.insert_list(table_name, odds, verbose=True)
				time.sleep(.1)
				entries.append(odds)
		#if count == 0:
		dt = dt + timedelta(days=1)
		dt8 = dt.strftime("%Y%m%d")
		count += 1

	df = pd.DataFrame(entries, columns=column_names)
	#df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
	print(df)

	bdb.close()


def main():
	run_odds()


if __name__ == "__main__":
	main()
