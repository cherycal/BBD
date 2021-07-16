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

	odds_date8 = utc_now.strftime("%Y%m%d")
	odds_update_time = utc_now.strftime("%Y%m%d%H%M%S")

	url = "https://sportsbook.draftkings.com/leagues/baseball/2003?category=game-lines-&subcategory=game"
	dfs = pd.read_html(url)
	tbl = dfs[0]

	entries = []
	column_names = ["date", "name", "time", "Tm", "Team", "OU", "ML", "UpdateTime"]
	table_name = "Odds"

	for i in dfs:
		oddslines = i.iloc[:, 0:4]
		for oddsline in oddslines.values:
			oddslist = process_oddsline(' '.join(map(str, oddsline)))
			print(oddslist)
			if len(oddslist) > 10:
				# print(oddslist)
				if any(char.isdigit() for char in oddslist[5]):
					name = f'{oddslist[3]} {oddslist[4]}'
				else:
					name = f'{oddslist[3]} {oddslist[4]} {oddslist[5]}'
				name = unidecode.unidecode(name)
				odds = list(itemgetter(0, 1, 2, -3, -1)(oddslist))
				odds.insert(0, name)
				odds.insert(0, odds_date8)
				odds.append(odds_update_time)
				#print(f'{odds}')
				bdb.insert_list(table_name, odds, verbose=True)
				time.sleep(.25)
				entries.append(odds)

	df = pd.DataFrame(entries, columns=column_names)
	#df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
	print(df)

	bdb.close()


def main():
	run_odds()


if __name__ == "__main__":
	main()
