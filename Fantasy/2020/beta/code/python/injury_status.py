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
    max_date  = str(max_date[0][0])
    print( max_date )
    print(integer_today)
    print(integer_yesterday)
    if max_date == out_date:
        msg += "\tThe process has already been run today, " + str(out_date) + ". The program is exiting.\n\n"
        #exit_process(1)
        exit(1)


def run_queries():


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
                                        " and ESPNID in ( Select ESPNID from PlayerData where "
                                        "InjuryStatus = 'ACTIVE' and Date = " + string_yesterday + ") "
                                        "order by InjuryStatus, AuctionValue desc")
    for r in just_added_to_dtd:
        print(r[2] + "\t, " + str(r[3]) + "\t, " + r[5] + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + str(r[10])  )

    print("\n\n")



    print("Just added to IL")
    just_added_to_il = bdb.select("select P.*, Team, LeagueID from PlayerData P "
                                        "left outer join Rosters R on P.Name = R.Player "
                                        "where InjuryStatus like '%DL%' and Date = " + string_today +
                                        " and ESPNID in ( Select ESPNID from PlayerData where "
                                        "InjuryStatus = 'ACTIVE' and Date = " + string_yesterday + ") "
                                        "order by InjuryStatus, AuctionValue desc")
    for r in just_added_to_il:
        print(r[2] + "\t, " + str(r[3]) + "\t, " + r[5] + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + str(r[10])  )

    print("\n\n")

    print("Just became active from IL")
    just_became_active_from_il = bdb.select("select P.*, Team, LeagueID from PlayerData P "
                                  "left outer join Rosters R on P.Name = R.Player "
                                  "where InjuryStatus = 'ACTIVE' and Date = " + string_today +
                                  " and ESPNID in ( Select ESPNID from PlayerData where "
                                  "InjuryStatus like '%DL%' and Date = " + string_yesterday + ") "
                                  "order by InjuryStatus, AuctionValue desc")
    for r in just_became_active_from_il:
        print(r[2] + "\t, " + str(r[3]) + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + str(r[10]))

    print("\n\n")
    print("Just became active from DTD")
    just_became_active_from_dtd = bdb.select("select P.*, Team, LeagueID from PlayerData P "
                                            "left outer join Rosters R on P.Name = R.Player "
                                            "where InjuryStatus = 'ACTIVE' and Date = " + string_today +
                                            " and ESPNID in ( Select ESPNID from PlayerData where "
                                            "InjuryStatus like 'DAY_TO_DAY' and Date = " + string_yesterday + ") "
                                            "order by InjuryStatus, AuctionValue desc")
    for r in just_became_active_from_dtd:
        print(r[2] + "\t, " + str(r[3]) + "\t, " + str(r[8]) + "\t, " + str(r[9]) + "\t, " + str(r[10]))


    return


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
        for command in insert_list:
            #print(command)
            bdb.insert(command)
        msg += "Total entries: " + str(entries) + "\n\n"



def exit_process(code):
    global msg, f, bdb
    msg += "Exit code: " + str(code) + "\n\n"
    print(msg)
    f.write(msg)
    f.close()
    bdb.close()
    exit(code)

def exit_silently():
    exit()

def main():
    global f, msg

    #msg += "Running injury status at " + date_time + "\n\n"
    #outfile = setup_outfile("injury_status")
    #f = open(outfile, "w")

    pd = load_position_dict()

    #check_position_dict(pd)

    #check_date()

    #get_teams()

    run_queries()

    #update_rosters()

    #exit_process(0)

    exit_silently()

if __name__ == "__main__":
    main()

