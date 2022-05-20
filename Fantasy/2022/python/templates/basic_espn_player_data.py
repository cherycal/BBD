import json
import sys

sys.path.append('../modules')
import pycurl
import certifi
from io import BytesIO


def main():
	#bdb = sqldb.DB('Baseball.db')
	yr = 2022

	dfheaders = ["Name", "id", "Year", "AuctionValue", "rank",
	             "AuctionValueAvg", "AuctionChange", "AB", "H", "AVG", "2B", "3B", "HR", "BB", "K",
	             "SLG", "OBP", "OPS", "R", "RBI", "SB", "GIDP",
	             "IPOUTS", "H_OPP", "HR_OPP", "ER", "K_OPP", "BB_OPP", "W", "L",
	             "WHIP", "ERA", "SV", "HD", "QS","RA","BS","BAA"]

	# dashes = ['NULL', yr, yr]
	# for i in range(35):
	# 	dashes.append(0)
	# print(dashes)

	#df = pd.DataFrame([dashes], columns=dfheaders)

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
		if player.get('player'):
			player_data = player['player']
			player_name = player_data.get('fullName',"NA")
			if player_data.get('stats'):
				print(f'Name: {player_name}')
				for stat in player_data['stats']:
					# 00: actual 10: projected
					if stat['id'] == '00' + str(yr):
						stats = stat['stats']
						if len(stats):
							print(f'Length: {len(stats)}: {stats}')

	#df = df.append(pd.DataFrame([pl], columns=df.columns))

	#df.to_csv(csv_file)

	#table_name = "ESPNProjections"

	#del_cmd = "delete from " + table_name + " where Year = " + str(yr)
	#bdb.delete( del_cmd)

	#df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

	#bdb.update("update ESPNProjections set PPTS = IPOUTS-H_OPP-BB_OPP+K_OPP-2*ER+W-L+5*SV+3*HD+2*QS")
	#bdb.update("update ESPNProjections set BPTS = H+'2B'+2*'3B'+3*HR+R+SB+RBI+BB-K")

	#bdb.close()
	exit(0)


if __name__ == "__main__":
	main()
