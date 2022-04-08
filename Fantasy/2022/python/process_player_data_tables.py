import sys
import time
from datetime import datetime

sys.path.append('./modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)


def main():
	# NEED TO ADD PROCEDURE: Move PlayerDataCurrent to PlayerData
	# insert into PlayerDataHistory select * from PlayerDataCurrent

	ts = datetime.now()  # current date and time
	out_time = ts.strftime("%Y%m%d-%H%M%S")
	print(out_time)

	fantasy.get_db_player_info()

	command = ""
	tries = 0
	TRIES_BEFORE_QUITTING = 3
	SLEEP = 5
	passed = 0
	while tries < TRIES_BEFORE_QUITTING:
		tries += 1
		try:
			command = "Delete from ESPNPlayerDataCurrent"
			bdb.delete(command)
			print("\nDelete ESPNPlayerDataCurrent worked\n")
			passed = 1
			break
		except Exception as ex:
			inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time), command + ": " + str(ex))
		time.sleep(SLEEP)

		if not passed:
			inst.push("DATABASE ERROR", command)

	insert_many_list = fantasy.get_espn_player_info()

	tries = 0
	passed = 0

	while tries < TRIES_BEFORE_QUITTING:
		tries += 1
		try:
			print(insert_many_list[0])
			bdb.insert_many("ESPNPlayerDataCurrent", insert_many_list)
			print("\ninsert ESPNPlayerDataCurrent worked\n")
			passed = 1
			break
		except Exception as ex:
			inst.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time),
			          "Insert ESPNPlayerDataCurrent" + ": " + str(ex))
		time.sleep(SLEEP)

	if not passed:
		inst.push("DATABASE ERROR", "insert ESPNPlayerDataCurrent")


if __name__ == "__main__":
	main()
