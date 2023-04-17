import json
import sys
import time
import urllib.request

sys.path.append('./modules')
import sqldb
import pandas as pd
import csv


def one_lg(bdb, lg, yr="0", update_db=0):
	url_name = "https://fantasy.espn.com/apis/v3/games/flb/leagueHistory/" + lg + "?" \
	                                                                              "view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav"
	if yr == "2020":
		url_name = "https://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + lg + "?" \
		                                "view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav"
	if yr == "2021" or yr == "2022":
		# url_name = "https://fantasy.espn.com/apis/v3/games/flb/seasons/2021/segments/0/leagues/" + lg +\
		#            "?view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav"
		url_name = f"https://fantasy.espn.com/apis/v3/games/flb/seasons/{yr}/segments/0/leagues/{lg}?view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav"
			# https://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/162788?view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav

	print(url_name)
	csv_file = "C:\\Users\chery\Documents\BBD\ESPN\\" + lg + "_draft.csv"
	print(csv_file)

	with urllib.request.urlopen(url_name) as url:
		json_object = json.loads(url.read().decode())

	headers = ["Year", "League", "autoDraftTypeId", "id", "bidAmount", "keeper", "lineupSlotId",
	           "memberId", "nominatingTeamId", "overallPickNumber", "owningTeamIds", "playerId",
	           "reservedForKeeper", "roundId", "roundPickNumber", "teamId", "tradeLocked"]

	# print(json.dumps(json_object, indent=4, sort_keys=True))
	pickinfo = []

	for i in json_object:
		count = 0
		print(url_name)
		print("Type: " + str(type(i)))
		print("i: " + str(i))
		if i == 'gameId':
			break
		if i == 'draftDetail':
			detail = json_object[i]
		else:
			detail = i['draftDetail']
		for pick in detail['picks']:
			print("-------------------------")
			print(count)
			print(pick)
			if detail.get('completeDate'):
				seconds = int(detail['completeDate']) / 1000.000
				draft_date = time.strftime("%Y%m%d", time.localtime(seconds))
				draft_yr = time.strftime("%Y", time.localtime(seconds))
				print("Date: " + str(draft_date))
				print("Year: " + str(draft_yr))
			else:
				draft_yr = "2018"
			bidAmount = pick.get('bidAmount', None)
			if lg == "37863846":
				bidAmount = None
			# time.sleep(2)
			pickrow = []
			pickrow.clear()
			pickrow.append(draft_yr)
			pickrow.append(lg)
			pickrow.append(pick.get('autoDraftTypeId', 0))
			pickrow.append(pick.get('id', 0))
			pickrow.append(bidAmount)
			pickrow.append(pick.get('keeper', 0))
			pickrow.append(pick.get('lineupSlotId', 0))
			pickrow.append(pick.get('memberId', 0))
			pickrow.append(pick.get('nominatingTeamId', 0))
			pickrow.append(pick.get('overallPickNumber', 0))
			pickrow.append(pick.get('owningTeamIds', ''))
			pickrow.append(pick.get('playerId', 0))
			pickrow.append(pick.get('reservedForKeeper', 0))
			pickrow.append(pick.get('roundId', 0))
			pickrow.append(pick.get('roundPickNumber', ''))
			pickrow.append(pick.get('teamId', ''))
			pickrow.append(pick.get('tradeLocked', 0))
			print(pickrow)
			pickinfo.append(pickrow.copy())
			pickrow.clear()
			count += 1

	file = open(csv_file, 'w', newline='')

	print("Pickinfo: ")
	print(pickinfo)

	with file:
		# identifying header
		header = headers
		writer = csv.DictWriter(file, fieldnames=header)
		writer.writeheader()

		# writing data row-wise into the csv file
		write = csv.writer(file)
		write.writerows(pickinfo)

	file.close()

	print(csv_file)
	df = pd.read_csv(csv_file)
	table_name = "ESPNDrafts"
	if update_db:
		df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


def main():
	bdb = sqldb.DB('Baseball.db')
	lg = "6455"
	#one_lg(bdb, lg)
	one_lg(bdb, lg, "2022", update_db=1)
	bdb.close()


if __name__ == "__main__":
	main()
