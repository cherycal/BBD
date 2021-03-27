import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path
import push

inst = push.Push()
bdb = sqldb.DB('Baseball.db')

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
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
    if platform == "Windows":
        outfile = current_dir + "\\logs\\" + outfile_name + "_" + str(date_time) + ".txt"

    elif platform == "Linux" or platform == "linux":
        outfile = current_dir + "/logs/" + outfile_name + "_" + str(date_time) + ".txt"
    else:
        print("OS platform " + platform + " isn't Windows or Linux. Exit.")
        msg += "\tOS platform " + platform + " isn't Windows or Linux. Exit." + "\n\n"
        exit_process(1)

    msg += "\toutfile name is " + outfile + "\n\n"

    return outfile


def load_position_dict():
    global msg
    position_dict = {}
    msg += "load_position_dict()\n\n"
    if path.exists("dict.pickle") and open("dict.pickle", "rb"):
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
    global msg
    for position_id in position_dict:
        print(str(position_id) + ", " + position_dict[position_id])


def get_player_data_max_date():
    global msg
    msg += "check_date()\n\n"
    max_date = bdb.select("SELECT max(Date) from ESPNPlayerData")
    return max_date


def check_for_new_players():
    global msg
    msg += "check_for_new_players()\n\n"
    c = bdb.select("select ESPNID, Name from ESPNMostRecentPlayerData where ESPNID not in (select ESPNID from ESPNPlayerData)")
    for t in c:
        print(t)
        msg += str(t) + "\n"
    return


def get_teams():
    global msg
    msg += "get_teams()\n\n"
    c = bdb.select("SELECT LeagueID, Name FROM ESPNLeagues where LeagueID = 6455")
    for t in c:
        league_dict[t[0]] = t[1]

    c = bdb.select("SELECT * FROM ESPNRosters where LeagueID  in (SELECT LeagueID FROM ESPNLeagues where Active = 'True')")
    for t in c:
        old_own_status[t[0] + ':' + t[1]] = t[1]
        team_dict[t[1]] = t[2]


def get_player_data_from_espn(position_dict):
    global msg
    msg += "get_player_data_from_espn()\n\n"
    season = "2021"

    for league_id in league_dict:
        print(league_id)
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/" + season + \
                   "/segments/0/leagues/" + str(league_id) + "?view=kona_player_info"
        print(url_name)
        with urllib.request.urlopen(url_name) as url:
            data = json.loads(url.read().decode())

        for player in data['players']:
            # print(player['player'])
            if 'ownership' in player['player']:
                if player['player']['ownership']['percentOwned'] >= 0:
                    full_name = player['player']['fullName']
                    espn_id = str(player['player']['id'])
                    auction_value = round(player['player']['ownership']['auctionValueAverage'], 2)
                    auction_value_change = str(round(player['player']['ownership']['auctionValueAverageChange'], 2))
                    percent_owned = round(player['player']['ownership']['percentOwned'], 2)
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

                    command = "INSERT INTO ESPNMostRecentPlayerData( Date, ESPNID, Name, PercentOwned, AuctionValue," \
                              "InjuryStatus, ESPNTEAMID, AuctionValueChange, EligibleSlots,UpdateTime,Bats, " \
                              "Throws, PrimaryPosition, NextStartID, MLBTeam, PercentStarted, AverageDraftPosition ) " \
                              "VALUES (" + str(out_date) + "," + str(espn_id) + ", " + \
                              "\"" + full_name + "\" ," + str(percent_owned) + ", " + \
                              str(auction_value) + ",\"" + injury_status + "\", " + str(pro_team_id) + ", " + str(
                        auction_value_change) + \
                              ",\"" + position_string + "\"," + str(date_time) + ",NULL,NULL,NULL,NULL,NULL,NULL,NULL)"

                    if auction_value > 0 or percent_owned > 0:
                        insert_list.append(command)


# noinspection PyRedundantParentheses
def update_most_recent_player_data_table(print_flag):
    global msg
    msg += "update_most_recent_player_data_table\n\n"
    entries = len(insert_list)
    minimum = 100

    if (entries < minimum):
        msg += "Not enough entries in new list: " + str(entries) + "\n\n"
        # inst.push("Roster error: " + str(date_time), msg)
        print(msg)
        exit_process(1)
    else:
        print("Updating ESPNMostRecentPlayerData table")
        msg += "Updating ESPNMostRecentPlayerData table" + "\n\n"
        bdb.delete("DELETE from ESPNMostRecentPlayerData")
        for command in insert_list:
            if print_flag:
                print(command)
            bdb.insert(command)
        msg += "Total entries: " + str(entries) + "\n\n"
    return


def check_number_of_new_most_recent_entries():
    global msg
    new_player_data_differences = 0

    msg += "check_number_of_new_most_recent_entries\n\n"

    rows = bdb.query(cmd="select M.*, P.InjuryStatus as OldInjuryStatus from ESPNMostRecentPlayerData M, ESPNPlayerData P "
                         "where M.Date = P.Date and M.ESPNID = P.ESPNID")
    existing_player_data_entries: int = int(len(rows))
    print("Number of existing_player_data_entries:")
    print(existing_player_data_entries)

    new_differences_list = list()
    if existing_player_data_entries != 0:
        rows = bdb.query("select M.*, P.InjuryStatus as OldInjuryStatus "
                         "from ESPNMostRecentPlayerData M, PlayerData P where M.Date = P.Date and M.ESPNID = P.ESPNID "
                         "and M.InjuryStatus != P.InjuryStatus order by PercentOwned desc")
        new_player_data_differences = int(len(rows))
        if existing_player_data_entries > 0 and new_player_data_differences > 0:
            for row in rows:
                row_str = str(row['Name']) + ', ' + str(row['ESPNID']) + ', ' + \
                          str(row['PercentOwned']) + ', ' + str(row['EligibleSlots']) + ', ' + \
                          str(row['InjuryStatus']) + ', ' + str(row['OldInjuryStatus']) + '\n'
                new_differences_list.append(row_str)
                print(row_str)
            print("\n\n")
        print("Number of new player data differences:")
        print(new_player_data_differences)
        if new_player_data_differences > 0:
            inst.push_list(new_differences_list, "New Updates:\n")

    return existing_player_data_entries, new_player_data_differences


def update_player_data_table(existing_entries, new_diffs):
    global msg
    if existing_entries == 0 or new_diffs > 0:
        print("Updating PlayerData with MostRecentPlayerData")
        print("Existing new entries in PlayerData table: " + str(existing_entries))
        print("New differences: " + str(new_diffs))
        msg += "update_player_data_table\n\n"
        bdb.delete("DELETE from ESPNPlayerData where Date = " + str(out_date))
        bdb.insert("INSERT into ESPNPlayerData select * from ESPNMostRecentPlayerData")
    return


def get_dtd():
    dtd_dict = {}
    dtd_players = bdb.select("select ESPNID from ESPNPlayerData where InjuryStatus like '%DAY_TO_DAY%' ")
    for player in dtd_players:
        dtd_dict[player] = player
    return dtd_dict


def get_dl():
    dl_dict = {}
    dl_players = bdb.select("select ESPNID from ESPNPlayerData where InjuryStatus like '%DL%' ")
    for player in dl_players:
        dl_dict[player] = player
    return dl_dict


def just_added_to_dtd(push_data):
    global msg
    print("just_added_to_dtd()")

    query = "select P.Date, P.ESPNID, P.Name, P.PercentOwned, P.AuctionValue, P.InjuryStatus" + \
            ", P.ESPNTEAMID, P.AuctionValueChange, P.EligibleSlots, P.UpdateTime, Team, LeagueID from ESPNPlayerData P " + \
            "left outer join ESPNRosters R on P.Name = R.Player " + \
            "where InjuryStatus = 'DAY_TO_DAY' and Date = " \
            + string_today + " and P.ESPNID in ( Select ESPNID from ESPNPlayerData where " + \
            "InjuryStatus = 'ACTIVE' and Date = " + string_yesterday + ") " + \
            "order by AuctionValue desc"

    # headers = bdb.table_cols(query)
    # print("Table cols: ")
    # for t in headers:
    #     print(t[0])

    added_to_dtd = bdb.select(query)

    injury_msg_list = list()
    for r in added_to_dtd:
        name = r[2]
        percent_owned = str(r[3])
        injury_status = r[5]
        eligible_slots = str(r[8])
        team = str(r[10])
        lg = str(r[11])
        if len(lg):
            lg = lg[0]
        print(
            name + "\t, " + percent_owned + "\t, " + injury_status + "\t, " + eligible_slots + "\t, " + team + "\t, " + lg)
        injury_msg_list.append(name + ', ' + percent_owned + ", " + eligible_slots + ", " + team + ", " + lg + "\n")
    print("\n\n")

    if len(injury_msg_list) > 0 and push_data:
        pass
        inst.push_list(injury_msg_list, "Added to DTD list: " + str(out_date))


def just_added_to_il(push_data):
    global msg
    print("just_added_to_il()")
    injury_msg_list = list()

    added_to_il = bdb.select("select P.Date, P.ESPNID, P.Name, P.PercentOwned, P.AuctionValue, P.InjuryStatus" +
                             ", P.ESPNTEAMID, P.AuctionValueChange, P.EligibleSlots, P.UpdateTime, Team, LeagueID from ESPNPlayerData P "
                             "left outer join ESPNRosters R on P.Name = R.Player "
                             "where InjuryStatus like '%DL%' and Date = " + string_today +
                             " and P.ESPNID in ( Select ESPNID from ESPNPlayerData where "
                             "InjuryStatus not like '%DL%' and Date = " + string_yesterday + ") "
                                                                                             "order by InjuryStatus, AuctionValue desc")

    for r in added_to_il:
        # espn_id = r[1]
        # if espn_id not in dl_dict:
        #    continue
        name = r[2]
        percent_owned = str(r[3])
        injury_status = r[5]
        eligible_slots = str(r[8])
        team = str(r[10])
        lg = str(r[11])
        if len(lg):
            lg = lg[0]

        print(name + "\t, " + percent_owned + "\t, " + injury_status + "\t, " +
              eligible_slots + "\t, " + team + "\t, " + lg)
        injury_msg_list.append(name + "\t, " + percent_owned + "\t, " + injury_status +
                               "\t, " + eligible_slots + ", " + team + ", " + lg + "\n")

    if len(injury_msg_list) > 0 and push_data:
        inst.push_list(injury_msg_list, "Added to IL list: " + str(out_date))


def just_activated_from_il(push_data):
    global msg
    print("just_activated_from_il()")
    injury_msg_list = list()

    active_from_il = bdb.select("select P.Date, P.ESPNID, P.Name, P.PercentOwned, P.AuctionValue, P.InjuryStatus" +
                                ", P.ESPNTEAMID, P.AuctionValueChange, P.EligibleSlots, P.UpdateTime, Team, LeagueID from ESPNPlayerData P "
                                "left outer join ESPNRosters R on P.Name = R.Player "
                                "where InjuryStatus not like '%DL%' and Date = " + string_today +
                                " and P.ESPNID in ( Select ESPNID from ESPNPlayerData where "
                                "InjuryStatus like '%DL%' and Date = " + string_yesterday + ") "
                                                                                            "order by InjuryStatus, AuctionValue desc")

    for r in active_from_il:
        name = r[2]
        percent_owned = str(r[3])
        eligible_slots = str(r[8])
        team = str(r[10])
        lg = str(r[11])
        if len(lg):
            lg = lg[0]
        print(name + "\t, " + percent_owned + "\t, " + eligible_slots + "\t, " + team + "\t, " + lg)
        injury_msg_list.append(name + "\t, " + percent_owned + "\t, " + eligible_slots + "\t, " + team + ", " + lg + "\n")

    if len(injury_msg_list) > 0 and push_data:
        inst.push_list(injury_msg_list, "Activated from IL list: " + str(out_date))


def just_activated_from_dtd(push_data):
    global msg
    print("just_activated_from_dtd()")
    injury_msg_list = list()

    active_from_dtd = bdb.select("select P.Date, P.ESPNID, P.Name, P.PercentOwned, P.AuctionValue, P.InjuryStatus" +
                                 ", P.ESPNTEAMID, P.AuctionValueChange, P.EligibleSlots, P.UpdateTime, Team, LeagueID from ESPNPlayerData P "
                                 "left outer join ESPNRosters R on P.Name = R.Player "
                                 "where InjuryStatus = 'ACTIVE' and Date = " + string_today +
                                 " and P.ESPNID in ( Select ESPNID from ESPNPlayerData where "
                                 "InjuryStatus like 'DAY_TO_DAY' and Date = " + string_yesterday + ") "
                                                                                                   "order by InjuryStatus, AuctionValue desc")

    for r in active_from_dtd:
        name = r[2]
        percent_owned = str(r[3])
        eligible_slots = str(r[8])
        team = str(r[10])
        lg = str(r[11])
        if len(lg):
            lg = lg[0]
        print(name + "\t, " + percent_owned + "\t, " + eligible_slots + "\t, " + team + "\t, " + lg)
        injury_msg_list.append(name + "\t, " + percent_owned + "\t, " + eligible_slots + "\t, " + team + ", " + lg + "\n")

    if len(injury_msg_list) > 0 and push_data:
        inst.push_list(injury_msg_list, "Activated from DTD: " + str(out_date))


def run_injury_queries(existing_entries):
    # dtd_dict = get_dtd()
    # dl_dict = get_dl()

    # for id in dtd_dict:
    # pass
    # print(id)

    # for id in dl_dict:
    # pass
    # print(id)

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
    push_data = True

    # Only process this if PlayerData hasn't been populated yet ( aka no existing entries )
    if existing_entries > 0:
        push_data = False

    just_added_to_dtd(push_data)

    just_added_to_il(push_data)

    just_activated_from_il(push_data)

    just_activated_from_dtd(push_data)

    return


# noinspection PyGlobalUndefined
def exit_process(code):
    global msg, bdb
    msg += "Exit code: " + str(code) + "\n\n"
    print(msg)
    exit(code)


def close_file_object(f):
    f.write(msg)
    f.close()
    bdb.close()


# noinspection PyUnreachableCode
def main():
    global msg

    msg += "Running player_ownership at " + date_time + "\n\n"

    outfile = setup_outfile("player_ownership")
    f = open(outfile, "w")

    # ESPN position ids to names
    pd = load_position_dict()

    # check_position_dict(pd)
    # get_player_data_max_date()

    check_for_new_players()

    # get Fantasy team data
    # league_dict and team_dict
    get_teams()

    get_player_data_from_espn(pd)

    update_most_recent_player_data_table(print_flag=False)

    (existing_entries, new_diffs) = check_number_of_new_most_recent_entries()

    update_player_data_table(existing_entries, new_diffs)

    run_injury_queries(existing_entries)

    close_file_object(f)

    exit_process(0)


if __name__ == "__main__":
    main()
