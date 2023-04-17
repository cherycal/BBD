import sys
import time

sys.path.append('./modules')
import fantasy
mode = "PROD"

fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()



def main():

	mylist = fantasy.get_espn_player_info()
	print(mylist)
	command = "Delete from ESPNPlayerDataCurrent"
	bdb.delete(command)
	time.sleep(.5)
	bdb.insert_many("ESPNPlayerDataCurrent", mylist)
	bdb.close()
	exit(0)


if __name__ == "__main__":
	main()
