import urllib.request, json
import sys
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

league_dict = {}
team_dict = {}
old_rosters = {}
new_rosters = {}
insert_list = []

#######################################################################################################################

def get_teams():

    c = bdb.select("SELECT LeagueID, Name FROM Leagues where Active = 'True'")
    for t in c:
        league_dict[t[0]] = t[1]

    c = bdb.select("SELECT * FROM Rosters where LeagueID  in (SELECT LeagueID FROM Leagues where Active = 'True')")
    for t in c:
        old_rosters[str(t[3]) + ':' + t[0]] = t[1]
        team_dict[t[1]] = t[2]

def print_teams():
    for league in league_dict:
        print( str(league) + ", " + league_dict[league])

def print_rosters():
    for key in old_rosters:
        print( key + ", " + old_rosters[key])


def get_new_rosters():

    for league in league_dict:
        addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(league) + "?view=roster"
        print(addr)

        with urllib.request.urlopen(addr) as url:
            data = json.loads(url.read().decode())

        for team in data['teams']:
            team_name = team['location'] + " " + team['nickname']
            for player in team['roster']['entries']:
                player_full_name = player['playerPoolEntry']['player']['fullName']
                espn_id = player['playerPoolEntry']['player']['id']
                command = "INSERT INTO Rosters(Player, Team, LeagueID, ESPNID) VALUES ( \"" + player_full_name + \
                          "\" ,\"" + team_name + "\"," + str(league) + "," + str(espn_id) + ")"
                new_rosters[str(espn_id) + ':' + player_full_name] = team_name
                #print(command)
                insert_list.append(command)
    return


def update_rosters():
    players = len(insert_list)

    minimum = 200

    if (players < minimum):
        print("Not enough players in new roster list: " + str(players))
        msg += "Not enough players in new roster list"
        inst.push("Roster error: " + str(date_time), msg)
        time.sleep(2)
        inst.push("Roster error: " + str(date_time), msg)
    else:
        print("New roster list appears to be full, number of players: " + str(players))
        print("Updating Rosters table")
        c = bdb.delete("DELETE FROM Rosters where LeagueID  in (SELECT LeagueID FROM Leagues where Active = 'True')")
        for command in insert_list:
            #print(command)
            bdb.insert(command)

def broadcast_changes():
    msg = ""
    for p in old_rosters:
        if new_rosters.get(p):
            if (old_rosters[p] == new_rosters[p]):
                # print(p, old_rosters[p], new_rosters[p] )
                pass
            else:
                # print("In old not in new: " + p, old_rosters[p], new_rosters[p] )
                msg += "DROPPED: " + p + ": " + old_rosters[p] + ", " + new_rosters[p]  + ".  "
                msg += "\n"
        else:
            # print("In old not in new: " + p)
            msg += "DROPPED: " + p
            msg += "\n"

    for p in new_rosters:
        if (old_rosters.get(p)):
            pass
        else:
            # print("In new not in old: " + p, new_rosters[p])
            msg += "ADDED: " + p
            msg += "\n"

    if (msg != ""):
        msg += "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "****************************************************************************************\n" + \
               "***************************************************************************************"
        print("Msg: " + msg)
        inst.push("Roster changes: " + str(date_time), msg)
        time.sleep(2)
        inst.push("Roster changes: " + str(date_time), "Done")
    else:
        msg = "No changes"
        inst.push("Roster changes: " + str(date_time), msg)
        print("Msg: " + msg)

    return msg


def setup_outfile(outfile_name):

    outfile = ""
    platform = tools.get_platform()
    current_dir = os.getcwd()
    if (platform == "Windows"):
        outfile = current_dir + "\\logs\\" + outfile_name + "_" + str(out_date) + ".txt"

    elif (platform == "Linux" or platform == "linux"):
        outfile = current_dir + "/logs/" + outfile_name + "_" + str(out_date) + ".txt"
    else:
        print("OS platform " + platform + " isn't Windows or Linux. Exit.")
        exit(1)

    print(outfile)
    return outfile

#######################################################################################################################

def main():

    outfile = setup_outfile("roster_changes")
    f = open(outfile, "w")

    get_teams()
    # print_teams()
    # print_rosters()
    get_new_rosters()
    update_rosters()
    msg = broadcast_changes()

    f.write(msg)
    f.close()

    bdb.close()

if __name__ == "__main__":
    main()
