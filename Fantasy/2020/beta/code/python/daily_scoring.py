import json
import os
import sys
import time
import urllib.request
from datetime import datetime
import pickle
import os.path
from os import path

sys.path.append('./modules')
import sqldb, tools
import push

inst = push.Push()
bdb = sqldb.DB('Baseball.db')

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
date_time_string: str = now.strftime("%Y%m%d-%H%M%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)

msg = ""
league_dict = {}
team_dict = {}
old_injury_status = {}
new_injury_status = {}
old_own_status = {}
new_own_status = {}
espn_position = {}
insert_list = []


def setup_outfile(outfile_name):
    global msg

    msg += "setup_outfile()\n\n"

    outfile = ""
    platform = tools.get_platform()
    current_dir = os.getcwd()
    if platform == "Windows":
        outfile = current_dir + "\\logs\\" + outfile_name + "_" + str(date_time_string) + ".txt"
        print(outfile)

    elif platform == "Linux" or platform == "linux":
        outfile = current_dir + "/logs/" + outfile_name + "_" + str(date_time_string) + ".txt"
    else:
        print("OS platform " + platform + " isn't Windows or Linux. Exit.")
        msg += "\tOS platform " + platform + " isn't Windows or Linux. Exit." + "\n\n"
        exit_process(1)

    msg += "\toutfile name is " + outfile + "\n\n"

    return outfile

def get_espn_position_map():
    global msg
    msg += "get_espn_position_map()\n\n"
    table = bdb.select("SELECT PositionID, Position FROM ESPNPositions")
    for row in table:
        position_id = str(row[0])
        position_name = str(row[1])
        espn_position[position_id] = position_name


def get_teams():
    global msg
    msg += "get_teams()\n\n"
    c = bdb.select("SELECT LeagueID, Name FROM Leagues")
    for t in c:
        league_id = t[0]
        team_dict[league_id] = {}
        my_team_name = t[1]
        league_dict[league_id] = my_team_name
        # get espn team_ids and names
        with urllib.request.urlopen(
                "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(
                    league_id)) as url:
            data = json.loads(url.read().decode())
            for team in data['teams']:
                #print( str(league_id) + ': ' + str(team['id']) + ': ' + team['location'] + ' ' + team['nickname'])
                team_dict[league_id][str(team['id'])] = str(team['location'] + ' ' + team['nickname'])



def get_espn_data():
    global msg
    msg += "get_espn_data()\n\n"

    # http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/162788?view=mScoreboard

    for league_id in league_dict:
        if league_id == 162788:
            with urllib.request.urlopen(
                    "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(
                        league_id) + "?view=mScoreboard") as url:
                data = json.loads(url.read().decode())

            for team_item in data['schedule'][0]['teams']:
                team_name = str(team_dict[league_id][str(team_item['teamId'])])
                team_name = team_name.replace(" ", "")

                start_day_points = team_item['totalPoints']
                current_points = team_item['totalPointsLive']
                today_points = current_points - start_day_points

                print( team_name + " teamID: " + str(team_item['teamId']) + ", daily points: " + str( today_points))
                print( team_name + " teamID: " + str(team_item['teamId']) + ", total points: " + str( current_points))

                for player_data in team_item['rosterForCurrentScoringPeriod']['entries']:
                    lineup_slot_id = str(player_data['lineupSlotId'])
                    lineup_slot = espn_position[lineup_slot_id]
                    espn_team = team_dict[league_id][str(team_item['teamId'])]
                    espn_name = player_data['playerPoolEntry']['player']['fullName']
                    espn_id = str(player_data['playerPoolEntry']['player']['id'])
                    player_daily_points = str(player_data['playerPoolEntry']['appliedStatTotal'])
                    print( date_time_string + ', ' + espn_team + ', ' +
                           espn_id + ', ' + espn_name + ', ' + lineup_slot + ', ' + player_daily_points)

            for team_item in data['schedule'][0]['teams']:
                current_points = team_item['totalPointsLive']
                print(str( current_points))



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

    msg += "Running player_ownership at " + date_time_string + "\n\n"

    # outfile = setup_outfile("player_ownership")
    # f = open(outfile, "w")

    get_espn_position_map()
    get_teams()
    get_espn_data()

    # close_file_object(f)

    #exit_process(0)


if __name__ == "__main__":
    main()
