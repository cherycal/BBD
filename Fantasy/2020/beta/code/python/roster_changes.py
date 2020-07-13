import urllib.request, json
import sys
import time
from datetime import datetime
import sys
sys.path.append('./modules')
import sqldb

def get_teams():

    c = bdb.select("SELECT LeagueID, Name FROM Leagues where Active = 'True'")
    for t in c:
        league_dict[t[0]] = t[1]

    c = bdb.select("SELECT * FROM Rosters where LeagueID  in (SELECT LeagueID FROM Leagues where Active = 'True')")
    for t in c:
        old_rosters[t[0] + ':' + t[1]] = t[1]
        team_dict[t[1]] = t[2]

def print_teams():
    for league in league_dict:
        print( str(league) + ", " + league_dict[league])

def print_rosters():
    for key in old_rosters:
        print( key + ", " + old_rosters[key])


def get_new_rosters():
    new_rosters = {}

    for league in league_dict:
        addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(league) + "?view=roster"
        print(addr)

        with urllib.request.urlopen(addr) as url:
            data = json.loads(url.read().decode())

        for team in data['teams']:
            team_name = team['location'] + " " + team['nickname']
            for player in team['roster']['entries']:
                player_full_name = player['playerPoolEntry']['player']['fullName']
                command = "INSERT INTO Rosters(Player, Team, LeagueID) VALUES ( \"" + player_full_name + \
                          "\" ,\"" \
                          + \
                          team_name + "\"," + str(league) + ")"
                new_rosters[player_full_name + ':' + team_name] = team_name
                print(command)
                insert_list.append(command)
    return


def update_rosters():
    players = len(insert_list)
    msg = ""
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
            print(command)
            bdb.insert(command)


import push
inst = push.Push()

bdb = sqldb.DB('Baseball.db')

now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%m%d%Y-%H%M%S")

league_dict = {}
team_dict = {}
old_rosters = {}
insert_list = []

get_teams()
print_teams()
print_rosters()
get_new_rosters()
update_rosters()