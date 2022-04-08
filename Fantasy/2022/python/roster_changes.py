import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import push

inst = push.Push()

# current date and time
now = datetime.now()
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%m%d%Y-%H%M%S")

msg = ""

league_dict = {}
team_dict = {}
old_rosters = {}
last_roster = {}
new_rosters = {}
insert_list = []
new_insert_list = []
new_delete_list = []
bdb = object
f = object

#######################################################################################################################

def set_espn_position_map():
        position = {}
        query = "select PositionID, Position from ESPNPositions"
        rows = bdb.query(query)
        for row in rows:
            position[str(row['PositionID'])] = str(row['Position'])
        return position

def clear_data_structures():
    league_dict.clear()
    team_dict.clear()
    old_rosters.clear()
    last_roster.clear()
    new_rosters.clear()
    insert_list.clear()
    new_insert_list.clear()
    new_delete_list.clear()

def start_db():
    global bdb
    bdb = sqldb.DB('Baseball.db')

def get_teams_and_rosters():
    c = bdb.select("SELECT LeagueID, Name FROM ESPNLeagues where Active = 'True'")
    for t in c:
        league_dict[t[0]] = t[1]

    c = bdb.select("SELECT * FROM ESPNRosters where LeagueID  in (SELECT LeagueID FROM ESPNLeagues where Active = 'True')")
    for t in c:
        espn_id = str(t[3])
        player_name = t[0]
        team_name = t[1]
        league_id = str(t[2])
        old_rosters[espn_id + ':' + team_name] = player_name + ", " + team_name + " (Lg " + league_id + ")"
        k = espn_id + ':' + team_name
        if last_roster.get(k):
            last_roster[k]['ID'] = espn_id
            last_roster[k]['leagueID'] = league_id
        else:
            last_roster[k] = {}
            last_roster[k]['ID'] = espn_id
            last_roster[k]['leagueID'] = league_id

        team_dict[team_name] = league_id


def print_teams():
    for league in league_dict:
        print(str(league) + ", " + league_dict[league])

def print_rosters():
    for key in old_rosters:
        print(key + ", " + old_rosters[key])


# def get_new_rosters():
#     for league in league_dict:
#         addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(
#             league) + "?view=roster"
#         print(addr)
#
#         with urllib.request.urlopen(addr) as url:
#             data = json.loads(url.read().decode())
#
#         for team in data['teams']:
#             team_name = team['location'] + " " + team['nickname']
#             for player in team['roster']['entries']:
#                 player_full_name = player['playerPoolEntry']['player']['fullName']
#                 espn_id = player['playerPoolEntry']['player']['id']
#                 command = "INSERT INTO Rosters(Player, Team, LeagueID, ESPNID) VALUES (\"" + player_full_name + \
#                           "\" ,\"" + team_name + "\"," + str(league) + "," + str(espn_id) + ")"
#                 new_rosters[str(espn_id) + ':' + team_name] = player_full_name + ", " + \
#                 team_name + " (Lg " + str(league) + ")"
#                 #print(command)
#                 insert_list.append(command)
#     return

def query_new_rosters():
    #inserts done here
    pos_map = set_espn_position_map()
    for league in league_dict:
        addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(
            league) + "?view=mRoster&view=mTeam&view=modular&view=mNav"
        print(addr)

        with urllib.request.urlopen(addr) as url:
            data = json.loads(url.read().decode())

        for team in data['teams']:
            team_name = team['location'] + " " + team['nickname']
            if 'roster' in team:
                for player in team['roster']['entries']:
                    #lineupslotid
                    player_full_name = player['playerPoolEntry']['player']['fullName']
                    #print(player_full_name + ": " + str(pos_map[str(player['lineupSlotId'])]))
                    pos = str(pos_map[str(player['lineupSlotId'])])
                    espn_id = player['playerPoolEntry']['player']['id']
                    command = "INSERT INTO ESPNRosters(Player, Team, LeagueID, ESPNID, Position) VALUES (\"" + player_full_name + \
                              "\" ,\"" + team_name + "\"," + str(league) + "," + str(espn_id) + ",\"" + pos + "\")"
                    k = str(espn_id) + ':' + team_name
                    v = player_full_name + ", " + team_name + " (Lg " + str(league) + ")"
                    new_rosters[k] = v
                    if not old_rosters.get(k):
                        #print("New insert: " + command)
                        new_insert_list.append(command)
    return

def run_inserts():
    for command in new_insert_list:
        print(command)
        bdb.insert(command)

def check_new_rosters():
    global msg
    players = len(new_rosters)

    minimum = 1100

    if players < minimum:
        print("Not enough players in new roster list: " + str(players))
        msg += "Not enough players in new roster list"
        inst.push("Roster error: " + str(date_time), msg)
        time.sleep(2)
        inst.push("Roster error: " + str(date_time), msg)
        exit(1)
    else:
        print("New roster list appears to be full, number of players: " + str(players))
        print("OK to update Rosters table")

def find_deletions():
    # deletes done here
    global msg
    msg = ""
    msg_list = list()
    for p in old_rosters:
        if new_rosters.get(p):
            if old_rosters[p] != new_rosters[p]:
                print("In old not in new: " + p, last_roster[p]['ID'], last_roster[p]['leagueID'])
                msg += "DROPPED: " + old_rosters[p] + ", " + new_rosters[p] + ".  "
                msg += "\n"
                msg_list.append("DROPPED: " + old_rosters[p] + ", " + new_rosters[p] + ".  " + "\n")
                delete_command = "DELETE from ESPNRosters where ESPNID = " + str(last_roster[p]['ID']) +\
                               " and LeagueID = " + str(last_roster[p]['leagueID'])
                new_delete_list.append(delete_command)
        else:
            # print("In old not in new: " + p)
            print("In old not in new: " + p, last_roster[p]['ID'], last_roster[p]['leagueID'])
            msg += "DROPPED: " + old_rosters[p]
            msg += "\n"
            msg_list.append("DROPPED: " + old_rosters[p] + "\n")
            delete_command = "DELETE from ESPNRosters where ESPNID = " + str(last_roster[p]['ID']) +\
                             " and LeagueID = " + str(last_roster[p]['leagueID'])
            new_delete_list.append(delete_command)
    for p in new_rosters:
        if old_rosters.get(p):
            pass
        else:
            # print("In new not in old: " + p, new_rosters[p])
            msg += "ADDED: " + new_rosters[p]
            msg += "\n"
            msg_list.append("ADDED: " + new_rosters[p] + "\n")

    return msg_list

def send_msg(msg_list):
    global msg
    if msg != "" and len(msg_list) < 500:
        msg += "****************************************************************************************\n"
        print("Msg: " + msg)
        # inst.push("Roster changes: " + str(date_time), msg)
        inst.push_list(msg_list, "Roster changes: " + str(date_time))
        time.sleep(2)
        # inst.push("Roster changes: " + str(date_time), "Done")
    else:
        msg = "No changes\n"
        # inst.push("Roster changes: " + str(date_time), msg)
        print("Msg: " + msg)


def run_deletes():
    for command in new_delete_list:
        print(command)
        bdb.delete(command)


def setup_outfile(outfile_name):
    global f
    outfile = ""
    platform = tools.get_platform()
    current_dir = os.getcwd()
    if platform == "Windows":
        outfile = current_dir + "\\logs\\" + outfile_name + "_" + str(out_date) + ".txt"

    elif platform == "Linux" or platform == "linux":
        outfile = current_dir + "/logs/" + outfile_name + "_" + str(out_date) + ".txt"
    else:
        print("OS platform " + platform + " isn't Windows or Linux. Exit.")
        exit(1)

    print(outfile)
    f = open(outfile, "w")
    f.close()
    return outfile

def log_append(outfile):
    global f
    f = open(outfile, "a")
    now2 = datetime.now()
    date_time2 = now2.strftime("%m/%d/%Y-%H:%M:%S")
    f.write(date_time2)
    f.write('\n')
    return

def close_db():
    bdb.close()

#######################################################################################################################

def main():

    global msg, f
    outfile = setup_outfile("roster_changes")

    start_db()

    now3 = datetime.now()
    date_time3 = now3.strftime("%m/%d/%Y-%H:%M:%S")
    print(date_time3)
    log_append(outfile)
    clear_data_structures()

    get_teams_and_rosters()
    query_new_rosters()
    check_new_rosters()
    msg_list = find_deletions()
    run_inserts()
    run_deletes()

    send_msg(msg_list)

    f.write(msg)
    f.close()

    close_db()


if __name__ == "__main__":
    main()
