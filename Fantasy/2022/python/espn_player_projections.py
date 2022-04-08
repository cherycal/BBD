import json
import sys

sys.path.append('./modules')
import sqldb
import pycurl
import certifi
from io import BytesIO
import pandas as pd


def main():
	bdb = sqldb.DB('Baseball.db')
	yr = 2022

	dfheaders = ["Name", "id", "Year", "AuctionValue", "rank",
	             "AuctionValueAvg", "AuctionChange", "AB", "H", "AVG", "2B", "3B", "HR", "BB", "K",
	             "SLG", "OBP", "OPS", "R", "RBI", "SB", "GIDP",
	             "IPOUTS", "H_OPP", "HR_OPP", "ER", "K_OPP", "BB_OPP", "W", "L",
	             "WHIP", "ERA", "SV", "HD", "QS","RA","BS","BAA"]

	dashes = ['NULL', yr, yr]
	for i in range(35):
		dashes.append(0)
	print(dashes)

	df = pd.DataFrame([dashes], columns=dfheaders)

	url_name = "https://fantasy.espn.com/apis/v3/games/flb/" \
	           "seasons/" + str(yr) + "/segments/0/leaguedefaults/1?view=kona_player_info"

	headers = ['authority: fantasy.espn.com',
	           'accept: application/json',
	           'x-fantasy-source: kona',
	           'x-fantasy-filter: {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS","ONTEAM"]},'
	           '"filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]}}}']

	print("get_player_data_json: " + url_name)
	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url_name)
	c.setopt(c.HTTPHEADER, headers)
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.CAINFO, certifi.where())
	c.perform()
	c.close()

	data = buffer.getvalue()

	csv_file = str(yr) + "proj.csv"
	# f = open(str(yr) + "proj.txt", "w")
	json_data = json.loads(data)
	# f.write(json.dumps(json_data))
	# f.close()

	for player in json_data['players']:
		pl = []
		# print(player['fullName'])
		pi = player['player']
		pl.append(pi['fullName'])
		# print("id: " + str(pi['id']))
		pl.append(pi['id'])
		pl.append(yr)
		try:
			# print("auction value: " + str(pi['draftRanksByRankType']['STANDARD']['auctionValue']))
			pl.append(pi['draftRanksByRankType']['STANDARD']['auctionValue'])
			pl.append(pi['draftRanksByRankType']['STANDARD']['rank'])
		except KeyError:
			pl.append(0)
			pl.append(0)
		try:
			pl.append(abs(pi['ownership']['auctionValueAverage']))
			pl.append(abs(pi['ownership']['auctionValueAverageChange']))
		except KeyError:
			pl.append(0)
			pl.append(0)
		proj = 0
		if pi.get('stats'):
			#print(pi['fullName'])
			for stat in pi['stats']:
				# 00: actual 10: projected
				if stat['id'] == '10' + str(yr):
					# if pi['lastName'] == "Staumont":
					# 	time.sleep(5)
					# 	pass
					proj = 1
					stats = stat['stats']
					# print(stats)
					pl.append(stats.get('0', 0))
					pl.append(stats.get('1', 0))
					pl.append(stats.get('2', 0))
					pl.append(stats.get('3', 0))
					pl.append(stats.get('4', 0))
					pl.append(stats.get('5', 0))
					pl.append(stats.get('10', 0))
					pl.append(stats.get('27', 0))
					pl.append(stats.get('9', 0))
					pl.append(stats.get('17', 0))
					pl.append(stats.get('18', 0))
					pl.append(stats.get('20', 0))
					pl.append(stats.get('21', 0))
					pl.append(stats.get('23', 0))
					pl.append(stats.get('26', 0))
					pl.append(stats.get('34', 0))
					pl.append(stats.get('37', 0))
					pl.append(stats.get('46', 0))
					pl.append(stats.get('45', 0))
					pl.append(stats.get('48', 0))
					pl.append(stats.get('39', 0))
					pl.append(stats.get('53', 0))
					pl.append(stats.get('54', 0))
					pl.append(stats.get('41', 0))
					pl.append(stats.get('47', 0))
					pl.append(stats.get('57', 0))
					pl.append(stats.get('60', 0))
					pl.append(stats.get('63', 0))
					pl.append(stats.get('44', 0))
					pl.append(stats.get('58', 0))
					pl.append(stats.get('38', 0))
			if not proj:
				pl.extend([0.0] * 31)
		else:
			pl.extend([0.0] * 31)

		df = df.append(pd.DataFrame([pl], columns=df.columns))

	df.to_csv(csv_file)

	table_name = "ESPNProjections"

	del_cmd = "delete from " + table_name + " where Year = " + str(yr)
	bdb.delete( del_cmd)

	df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

	bdb.update("update ESPNProjections set PPTS = IPOUTS-H_OPP-BB_OPP+K_OPP-2*ER+W-L+5*SV+3*HD+2*QS")
	bdb.update("update ESPNProjections set BPTS = H+'2B'+2*'3B'+3*HR+R+SB+RBI+BB-K")

	bdb.close()
	exit(0)


if __name__ == "__main__":
	main()
