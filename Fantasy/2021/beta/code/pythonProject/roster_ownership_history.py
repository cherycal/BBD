import urllib.request, json
import time
from datetime import datetime
import sys
import os
sys.path.append('./modules')
import sqldb, tools

import push
inst = push.Push()
bdb = sqldb.DB('Baseball.db')

now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%m%d%Y-%H%M%S")
start_date = 20200713

league_dict = {}
team_dict = {}
old_injury_status = {}
new_injury_status = {}
old_own_status = {}
new_own_status = {}
insert_list = []
msg = ""

def setup_outfile(outfile_name):
    global msg

    msg += "setup_outfile()\n\n"

    outfile = ""
    platform = tools.get_platform()
    current_dir = os.getcwd()
    if (platform == "Windows"):
        outfile = current_dir + "\\logs\\" + outfile_name + "_" + str(out_date) + ".txt"

    elif (platform == "Linux" or platform == "linux"):
        outfile = current_dir + "/logs/" + outfile_name + "_" + str(out_date) + ".txt"
    else:
        print("OS platform " + platform + " isn't Windows or Linux. Exit.")
        msg += "\tOS platform " + platform + " isn't Windows or Linux. Exit." + "\n\n"
        exit_process(1)

    msg += "\toutfile name is " + outfile +"\n\n"
    return outfile



def get_teams():
    global msg

    msg += "get_teams()\n\n"

    c = bdb.select("SELECT LeagueID, Name FROM Leagues where Active = 'True'")
    for t in c:
        league_dict[t[0]] = t[1]

    c = bdb.select("SELECT * FROM Rosters where LeagueID  in (SELECT LeagueID FROM Leagues where Active = 'True')")
    for t in c:
        old_own_status[t[0] + ':' + t[1]] = t[1]
        team_dict[t[1]] = t[2]




def get_history():
    global msg

    msg += "get_history()\n\n"

    for league_id in league_dict:

        with urllib.request.urlopen("http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(league_id) + "?view=roster") as url:
            data = json.loads(url.read().decode())

        for team in data['teams']:
            team_name = team['location'] + " " + team['nickname']
            for player in team['roster']['entries']:
                player_full_name = player['playerPoolEntry']['player']['fullName']
                #print( player['playerPoolEntry']['player']['fullName'] )
                #print( player['playerPoolEntry'].keys() )
                for pool_entry_key in player['playerPoolEntry'].keys():
                    #print( pool_entry_key )
                    if pool_entry_key != "player":
                        pass
                        #print( player['playerPoolEntry'][pool_entry_key])
                    else:
                        #print( player['playerPoolEntry'][pool_entry_key].keys())
                        for player_key in player['playerPoolEntry']['player'].keys():
                            #print(player_key)
                            if player_key == "injuryStatus":
                                injury_status = player['playerPoolEntry']['player'][player_key]
                                #print(team_name + " , " + player_full_name + ", " + injury_status)
                            if player_key != "ownershipHistory":
                                pass
                                #print(player_key)
                                #print(player['playerPoolEntry']['player'][player_key])
                            else:
                                for item in player['playerPoolEntry']['player'][player_key]:
                                    item_date = time.localtime(item['date'] / 1000)
                                    history_date = time.strftime('%Y%m%d', item_date)
                                    percent_owned = round(item['percentOwned'],2)
                                    auction_value = round(item['auctionValueAverage'],2)
                                    #print(team_name + " , " + player_full_name + " , " + history_date + " , " +
                                    #    str(percent_owned) + " , " + str(auction_value))
                                    if int(history_date) > start_date:
                                        command = "INSERT INTO OwnershipHistory(Team, LeagueId, Player, Date, PercentOwned, AuctionValue) " \
                                                  "VALUES ( \"" + team_name + "\" ," + str(league_id) + ", " + \
                                                    "\"" + player_full_name + "\",\"" +  str(history_date)  + "\" ," + str(percent_owned) + ", " + \
                                                    str(auction_value) + ")"
                                        #print(command)
                                        insert_list.append(command)


def update_table():
    global msg

    msg += "update_table()\n\n"
    entries = len(insert_list)
    minimum = 100

    if (entries < minimum):
        print("Not enough entries in new list: " + str(entries))
        msg += "Not enough players in new roster list"
        #inst.push("Roster error: " + str(date_time), msg)
    else:
        print("Updating OwnershipHistory table")

        delete_command = "DELETE FROM OwnershipHistory where Date > " + str(start_date)
        print(delete_command)
        c = bdb.delete(delete_command)
        for command in insert_list:
            print(command)
            bdb.insert(command)


def exit_process(code):
    global msg, f, bdb
    msg += "Exit code: " + str(code) + "\n\n"
    f.write(msg)
    f.close()
    bdb.close()
    exit(code)

def main():

    global msg, f
    msg += "Running player_ownership at " + date_time + "\n\n"
    outfile = setup_outfile("player_ownership_history")
    f = open(outfile, "w")

    get_teams()
    get_history()
    update_table()

    exit_process(0)


if __name__ == "__main__":
    main()

