import urllib.request, json
import time
from datetime import datetime
import sys
import os
sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path
import push
inst = push.Push()
bdb = sqldb.DB('Baseball.db')

now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

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


def load_position_dict():
    global  msg
    position_dict = {}
    msg += "load_position_dict()\n\n"
    if path.exists("dict.pickle") and open("dict.pickle","rb"):
        msg += "Load from pickle\n\n"
        pickle_in = open("dict.pickle", "rb")
        position_dict = pickle.load(pickle_in)
    else:
        msg += "Load from DB\n\n"
        c = bdb.select("SELECT PositionID, Position from ESPNPositions")
        for t in c:
            position_dict[t[0]] = t[1]
    pickle_out = open("dict.pickle", "wb")
    pickle.dump(position_dict, pickle_out)
    pickle_out.close()
    return position_dict


def check_position_dict(position_dict):
    global  msg
    for position_id in position_dict:
        print( str(position_id ) + ", " + position_dict[position_id] )



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
    c = bdb.select("SELECT LeagueID, Name FROM Leagues where LeagueID = 6455")
    for t in c:
        league_dict[t[0]] = t[1]

    c = bdb.select("SELECT * FROM Rosters where LeagueID  in (SELECT LeagueID FROM Leagues where Active = 'True')")
    for t in c:
        old_own_status[t[0] + ':' + t[1]] = t[1]
        team_dict[t[1]] = t[2]


def get_history(position_dict):
    global msg
    msg += "get_history()\n\n"

    for league_id in league_dict:

        with urllib.request.urlopen("http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(league_id) + "?view=kona_player_info") as url:
            data = json.loads(url.read().decode())

        for player in data['players']:
            if player['player']['ownership']['percentOwned'] >= 0:
                full_name =  player['player']['fullName']
                espn_id = str(player['player']['id'])
                auction_value = round( player['player']['ownership']['auctionValueAverage'], 2)
                auction_value_change = str(round(player['player']['ownership']['auctionValueAverageChange'], 2))
                percent_owned = round( player['player']['ownership']['percentOwned'], 2)
                eligible_slots = player['player']['eligibleSlots']
                position_list = []
                for position_id in eligible_slots:
                    if position_id < 16 and position_id != 12:
                        position_list.append(position_dict[position_id])
                position_string = str(position_list)[1:-1]
                if 'injuryStatus' in player['player']:
                    injury_status = player['player']['injuryStatus']
                else:
                    injury_status = "NONE"
                pro_team_id = str(player['player']['proTeamId'])
                command = "INSERT INTO PlayerData( Date, ESPNID, Name, PercentOwned, AuctionValue," \
                          "InjuryStatus, ESPNTEAMID, AuctionValueChange, EligibleSlots) " \
                          "VALUES (" + str(out_date) + "," + str(espn_id) + ", " + \
                          "\"" + full_name + "\" ," + str(percent_owned) + ", " + \
                          str(auction_value) + ",\"" +  injury_status  + "\", " + str(pro_team_id) +  ", " + str(auction_value_change)  + \
                          ",\"" + position_string + "\")"
                #print(command)
                #print(str(eligible_slots))
                if auction_value > 0 or percent_owned > 0:
                    insert_list.append(command)




def update_rosters():
    global msg
    msg += "update_rosters()\n\n"
    entries = len(insert_list)
    minimum = 100

    if (entries < minimum):
        msg += "Not enough entries in new list: " + str(entries) + "\n\n"
        #inst.push("Roster error: " + str(date_time), msg)
        print(msg)
        exit_process(1)
    else:
        print("Updating PlayerData table")
        msg += "Updating PlayerData table" + "\n\n"
        bdb.delete("DELETE from PlayerData where Date = " + str(out_date))
        for command in insert_list:
            #print(command)
            bdb.insert(command)
        msg += "Total entries: " + str(entries) + "\n\n"

def get_dtd():
    dtd_dict = {}
    dtd_players = bdb.select("select ESPNID from PlayerData where InjuryStatus like '%DAY_TO_DAY%' ")
    for player in dtd_players:
        dtd_dict[player] = player
    return dtd_dict

def get_dl():
    dl_dict = {}
    dl_players = bdb.select("select ESPNID from PlayerData where InjuryStatus like '%DL%' ")
    for player in dl_players:
        dl_dict[player] = player
    return dl_dict

def run_injury_queries( push_data ):

    dtd_dict = get_dtd()
    dl_dict = get_dl()

    for id in dtd_dict:
        pass
        #print(id)

    for id in dl_dict:
        pass
        #print(id)


    # print("Just inactivated")
    # just_inactivated = bdb.select("select P.*, Team, LeagueID from PlayerData P "
    #                                     "left outer join Rosters R on P.Name = R.Player "
    #                                     "where InjuryStatus != 'ACTIVE' and Date = " + string_today +
    #                                     " and ESPNID in ( Select ESPNID from PlayerData where "
    #                                     "InjuryStatus = 'ACTIVE' and Date = " + string_yesterday + ") "
    #                                     "order by InjuryStatus, AuctionValue desc")
    # for r in just_inactivated:
    #     print(r[2] + ", " + str(r[3]) + ", " + r[5] + ", " + str(r[8]) + ", " + str(r[9]) + ", " + str(r[10])  )
    #
    #
    # print("\n\n")

    print( "Just added to Day to Day")
    just_added_to_dtd = bdb.select("select P.*, Team, LeagueID from PlayerData P "
                                        "left outer join Rosters R on P.Name = R.Player "
                                        "where InjuryStatus = 'DAY_TO_DAY' and Date = " + string_today +
                                        " and P.ESPNID in ( Select ESPNID from PlayerData where "
                                        "InjuryStatus = 'ACTIVE' and Date = " + string_yesterday + ") "
                                        "order by InjuryStatus, AuctionValue desc")
    injury_msg = ""
    for r in just_added_to_dtd:
        lg = str(r[10])
        if len(lg):
            lg = lg[0]
        print(r[2] + "\t, " + str(r[3]) + "\t, " + r[5] + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + lg)
        injury_msg += r[2] + ", " + str(r[9]) + ", " + lg + "\n"
    print("\n\n")

    if injury_msg != "" and push_data:
        pass
        inst.push("Added to DTD: " + str(out_date), injury_msg)

    print("Just added to IL")
    just_added_to_il = bdb.select("select P.*, Team, LeagueID from PlayerData P "
                                        "left outer join Rosters R on P.Name = R.Player "
                                        "where InjuryStatus like '%DL%' and Date = " + string_today +
                                        " and P.ESPNID in ( Select ESPNID from PlayerData where "
                                        "InjuryStatus not like '%DL%' and Date = " + string_yesterday + ") "
                                        "order by InjuryStatus, AuctionValue desc")

    injury_msg = ""
    count = 1
    for r in just_added_to_il:
        espn_id = r[1]
        #if espn_id not in dl_dict:
        #    continue

        lg = str(r[10])
        if len(lg):
            lg = lg[0]

        # Date
        # ESPNID
        # Name
        # PercentOwned
        # AuctionValue
        # InjuryStatus
        # ESPNTEAMID
        # AuctionValueChange
        # EligibleSlots
        # Team
        # LeagueId

        print(r[2] + "\t, " + str(r[3]) + "\t, " + r[5] + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + lg )
        injury_msg += r[2] + "\t, " + str(r[3]) + "\t, " + r[5] + "\t, " + str(r[8]) + "\t, " + str(r[9]) + ", " + lg + "\n"

        if count % 6 == 0 and push_data:
            inst.push("Added to IL: " + str(out_date), injury_msg)
            injury_msg = ""
        count += 1

    if injury_msg != "" and push_data:
        pass
        inst.push("Added to IL: " + str(out_date), injury_msg)

    print("\n\n")

    print("Just became active from IL")
    just_became_active_from_il = bdb.select("select P.*, Team, LeagueID from PlayerData P "
                                  "left outer join Rosters R on P.Name = R.Player "
                                  "where InjuryStatus not like '%DL%' and Date = " + string_today +
                                  " and P.ESPNID in ( Select ESPNID from PlayerData where "
                                  "InjuryStatus like '%DL%' and Date = " + string_yesterday + ") "
                                  "order by InjuryStatus, AuctionValue desc")

    injury_msg = ""
    count = 1
    for r in just_became_active_from_il:
        lg = str(r[10])
        if len(lg):
            lg = lg[0]
        print(r[2] + "\t, " + str(r[3]) + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + lg)
        injury_msg += r[2] + "\t, " + str(r[3]) + "\t, " + str(r[8]) + "\t, " + str(r[9]) + ", " + lg + "\n"
        if count % 6 == 0 and push_data:
            inst.push("Activated from IL: " + str(out_date), injury_msg)
            injury_msg = ""
        count += 1

    if injury_msg != "" and push_data:
        pass
        inst.push("Activated from IL: " + str(out_date), injury_msg)


    print("\n\n")

    print("Just became active from DTD")
    just_became_active_from_dtd = bdb.select("select P.*, Team, LeagueID from PlayerData P "
                                            "left outer join Rosters R on P.Name = R.Player "
                                            "where InjuryStatus = 'ACTIVE' and Date = " + string_today +
                                            " and P.ESPNID in ( Select ESPNID from PlayerData where "
                                            "InjuryStatus like 'DAY_TO_DAY' and Date = " + string_yesterday + ") "
                                            "order by InjuryStatus, AuctionValue desc")
    injury_msg = ""
    for r in just_became_active_from_dtd:
        lg = str(r[10])
        if len(lg):
            lg = lg[0]
        print(r[2] + "\t, " + str(r[3]) + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + lg)
        injury_msg += r[2] + "\t, " + str(r[4]) + "\t, " + str(r[8]) + "\t, " + str(r[9]) + ", " + lg + "\n"

    if injury_msg != "" and push_data:
        pass
        inst.push("Activated from DTD: " + str(out_date), injury_msg)

    return




def exit_process(code):
    global msg, f, bdb
    msg += "Exit code: " + str(code) + "\n\n"
    print(msg)
    f.write(msg)
    f.close()
    bdb.close()
    exit(code)

def main():
    global f, msg

    msg += "Running player_ownership at " + date_time + "\n\n"
    outfile = setup_outfile("player_ownership")
    f = open(outfile, "w")

    pd = load_position_dict()

    #check_position_dict(pd)

    #check_date()

    get_teams()

    get_history(pd)

    update_rosters()

    run_injury_queries(True)

    exit_process(0)

if __name__ == "__main__":
    main()

