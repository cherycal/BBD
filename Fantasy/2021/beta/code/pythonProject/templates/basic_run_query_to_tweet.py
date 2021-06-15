__author__ = 'chance'
import sys
sys.path.append('../modules')
import sqldb
import fantasy


fantasy = fantasy.Fantasy()

mode = "TEST"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

espnid_list = list()
espnid_list.append(31815)
espnid_list.append(35241)
print(str(tuple(espnid_list)))

query = f'select Player, Team, LeagueID,Position from ESPNRosters' \
						f' where espnid in {str(tuple(espnid_list))} order by Player, Team'

print(query)
try:
    fantasy.run_query(query, "Revelant rosters: ")
except Exception as ex:
    fantasy.push_instance.push("Error in relevant roster query", "Error: " + str(ex))
