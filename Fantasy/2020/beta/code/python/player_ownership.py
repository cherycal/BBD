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
out_date = now.strftime("%Y%m%d")

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


def check_date():
    global msg
    msg += "check_date()\n\n"

    max_date = bdb.select("SELECT max(Date) from PlayerData")
    if str(max_date[0][0]) == out_date:
        msg += "\tThe process has already been run today, " + str(out_date) + ". The program is exiting.\n\n"
        exit_process(1)



def get_teams():
    global msg
    msg += "get_teams()\n\n"
    c = bdb.select("SELECT LeagueID, Name FROM Leagues where LeagueID = 87301")
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

        with urllib.request.urlopen("http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(league_id) + "?view=players") as url:
            data = json.loads(url.read().decode())

        for player in data['players']:
            if player['player']['ownership']['percentOwned'] >= 0:
                full_name =  player['player']['fullName']
                espn_id = str(player['player']['id'])
                auction_value = str( round( player['player']['ownership']['auctionValueAverage'], 2) )
                auction_value_change = str(round(player['player']['ownership']['auctionValueAverageChange'], 2))
                percent_owned = str( round( player['player']['ownership']['percentOwned'], 2) )
                if 'injuryStatus' in player['player']:
                    injury_status = player['player']['injuryStatus']
                else:
                    injury_status = "NONE"
                pro_team_id = str(player['player']['proTeamId'])
                transactions = player['transactions']
                #print( out_date + ", " + full_name + ", " + espn_id+ ", " +
                #      auction_value + ", " + percent_owned + ", " + injury_status + ", " + pro_team_id  )
                command = "INSERT INTO PlayerData( Date, ESPNID, Name, PercentOwned, AuctionValue, InjuryStatus, ESPNTEAMID, AuctionValueChange) " \
                          "VALUES (" + str(out_date) + "," + str(espn_id) + ", " + \
                          "\"" + full_name + "\" ," + str(percent_owned) + ", " + \
                          str(auction_value) + ",\"" +  injury_status  + "\", " + str(pro_team_id) +  ", " + str(auction_value_change)  + ")"
                #print(command)
                #insert_list.append(command)
                if len(transactions) > 0:
                    pass
                    #print(transactions)



def update_rosters():
    global msg
    msg += "update_rosters()\n\n"
    entries = len(insert_list)
    msg = ""
    minimum = 100

    if (entries < minimum):
        print("Not enough entries in new list: " + str(entries))
        msg += "\tNot enough players in new list"
        #inst.push("Roster error: " + str(date_time), msg)
    else:
        print("Updating OwnershipHistory table")
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
    outfile = setup_outfile("player_ownership")
    f = open(outfile, "w")

    check_date()

    get_teams()

    get_history()

    update_rosters()

    exit_process(0)

if __name__ == "__main__":
    main()

