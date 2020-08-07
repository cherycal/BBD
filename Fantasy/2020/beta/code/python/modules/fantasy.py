__author__ = 'chance'

import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools, fantasy
import pickle
import os.path
from os import path
import push


class Fantasy(object):

    def __init__(self):
        db = 'Baseball.db'
        self.platform = tools.get_platform()
        if self.platform == "Windows":
            self.db = 'C:\\Ubuntu\\Shared\\data\\' + db
        elif self.platform == "linux" or self.platform == 'Linux':
            self.db = '/media/sf_Shared/data/' + db
        else:
            print("Platform " + self.platform + " not recognized in sqldb::DB. Exiting.")
            exit(-1)
        self.msg = "Msg: "
        self.DB = sqldb.DB(db)
        self.push_instance = push.Push()
        self.teamName = self.set_ID_team_map()
        self.MLBTeamName = self.set_ESPN_MLB_team_map()
        self.ownerTeam = self.set_owner_team_map()
        self.position2 = self.set_ESPN_position_map()
        self.position = self.load_position_dict()
        self.player, self.player_team = self.set_espn_player()
        # self.espn_player_json = self.set_espn_player_json()
        self.espn_trans_ids = self.get_espn_trans_ids()
        self.leagues = self.get_leagues()
        self.active_leagues = self.get_active_leagues()
        self.default_league = self.set_espn_default_league()
        self.str = ""

    def league_standings(self):
        leagueID = self.default_league
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID) + "?view=standings"
        print(url_name)
        with urllib.request.urlopen(url_name) as url:
            pass
            json_object = json.loads(url.read().decode())
            # json_formatted = json.dumps(json_object, indent=2)
            # print(json_formatted)
        return json_object

    def string_from_list(self, in_list, delimiter=''):
        s = ""
        for i in in_list:
            s += str(i)
            s += delimiter

        self.str = s[:-1]
        return self.str

    def get_espn_player_json(self):
        return self.espn_player_json

    def espn_player_name(self):
        return self.player

    def espn_player_mlb_team(self):
        return self.player_team

    def espn_position_map(self):
        return self.position2

    def owner_team_map(self):
        return self.ownerTeam

    def mlb_team_name_map(self):
        return self.MLBTeamName

    def team_name_map(self):
        return self.teamName

    def DB(self):
        return self.DB()

    def push_instance(self):
        return self.push_instance()

    def get_msg(self):
        return self.msg

    def set_msg(self, msg):
        self.msg = msg
        return 0

    def append_msg(self, msg):
        self.msg += msg
        return 0

    def get_active_leagues(self):
        leagues = {}
        query = "select distinct LeagueID from Leagues where Active = 'True'"
        rows = self.DB.query(query)
        for row in rows:
            leagues[str(row['LeagueID'])] = str(row['LeagueID'])[0]
        return leagues

    def set_ESPN_MLB_team_map(self):
        teamName = {}
        query = "select MLBTeamID, MLBTeam from ESPNMLBTeams"
        rows = self.DB.query(query)
        for row in rows:
            teamName[str(row['MLBTeamID'])] = str(row['MLBTeam'])
        return teamName

    def set_espn_player(self):
        player = {}
        player_team = {}
        query = "select ESPNID, Name, MLBTeam from MostRecentPlayerData M, ESPNMLBTeams E where M.ESPNTEAMID = E.MLBTeamID"
        rows = self.DB.query(query)
        for row in rows:
            player[str(row['ESPNID'])] = str(row['Name'])
            player_team[str(row['ESPNID'])] = str(row['MLBTeam'])
        return player, player_team

    def set_espn_player_json(self):
        leagueID = self.default_league
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID) + "?view=kona_playercard"
        print(url_name)
        with urllib.request.urlopen(url_name) as url:
            pass
            json_object = json.loads(url.read().decode())
            # json_formatted = json.dumps(json_object, indent=2)
        return json_object

    def set_ESPN_position_map(self):
        position = {}
        query = "select PositionID, Position from ESPNPositions"
        rows = self.DB.query(query)
        for row in rows:
            position[str(row['PositionID'])] = str(row['Position'])
        return position

    def get_espn_trans_ids(self):
        espn_trans_ids = {}
        query = "select distinct ESPNTransID from RosterChanges"
        rows = self.DB.query(query)
        for row in rows:
            espn_trans_ids[row['ESPNTransID']] = row['ESPNTransID']
        return espn_trans_ids

    def set_ID_team_map(self):
        teamName = dict()
        query = "select distinct LeagueID, TeamID, TeamName from ESPNTeamOwners"
        rows = self.DB.query(query)
        for row in rows:
            if str(row['LeagueID']) not in teamName:
                teamName[str(row['LeagueID'])] = {}
            teamName[str(row['LeagueID'])][str(row['TeamID'])] = str(row['TeamName'])
        return teamName

    def get_leagues(self):
        leagues = {}
        query = "select distinct LeagueID from Leagues"
        rows = self.DB.query(query)
        for row in rows:
            leagues[str(row['LeagueID'])] = str(row['LeagueID'])[0]
        return leagues

    def set_owner_team_map(self):
        teamName = {}
        query = "select OwnerID, TeamName from ESPNTeamOwners"
        rows = self.DB.query(query)
        for row in rows:
            teamName[str(row['OwnerID'])] = str(row['TeamName'])
        return teamName

    def fill_transaction_base(self, transaction_base, json_object,):
        return transaction_base

    def fill_item_list(self, transaction_base, transaction_summary):
        return item_list

    def get_transactions2(self, leagueID):
        pass

    def get_transactions(self, leagueID):
        self.espn_trans_ids = self.get_espn_trans_ids()
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID) + "?view=mTransactions2"
        #print(url_name)

        with urllib.request.urlopen(url_name) as url:
            json_object = json.loads(url.read().decode())
            push_list = list()
            transaction_base = list()
            transaction_summary = list()

            if 'transactions' in json_object:
                for transaction in json_object['transactions']:
                    transaction_base.clear()
                    transaction_summary.clear()
                    espn_transaction_id = transaction['id']
                    transaction_base.append(espn_transaction_id)

                    seconds = int(transaction['proposedDate']) / 1000.000
                    update_date = time.strftime("%Y%m%d", time.localtime(seconds))
                    transaction_base.append(update_date)
                    update_time = time.strftime("%H%M%S", time.localtime(seconds))
                    transaction_base.append(update_time)
                    update_datetime = time.strftime("%Y%m%d%H%M%S", time.localtime(seconds))

                    team_id = self.teamName[str(leagueID)][str(transaction['teamId'])]
                    transaction_base.append(team_id)
                    transaction_base.append(transaction['status'])
                    transaction_base.append(transaction['type'])

                    if 'transactions' in json_object:
                        item_count = 0
                        if 'items' in transaction:
                            for i in transaction['items']:
                                transaction_summary.extend(transaction_base)
                                item_list = list()
                                item_count += 1

                                transaction_id = espn_transaction_id + str(item_count)
                                # i_formatted = json.dumps(i, indent=2)
                                # print(i_formatted)
                                item_list.append(transaction_id)

                                from_position = ""
                                if int(i['fromLineupSlotId']) > 0:
                                    from_position = self.position[i['fromLineupSlotId']]
                                    item_list.append(from_position)
                                else:
                                    item_list.append("")

                                from_team = ""
                                if i['fromTeamId'] > 0:
                                    from_team = self.teamName[str(leagueID)][str(i['fromTeamId'])]
                                    item_list.append(from_team)
                                else:
                                    item_list.append("")

                                player_name = self.player[str(i['playerId'])]
                                item_list.append(player_name)

                                to_position = ""
                                if int(i['toLineupSlotId']) > 0:
                                    to_position = self.position[i['toLineupSlotId']]
                                    item_list.append(to_position)
                                else:
                                    item_list.append("")

                                to_team = ""
                                if 'toTeamId' in i and i['toTeamId'] > 0:
                                    to_team = self.teamName[str(leagueID)][str(i['toTeamId'])]
                                    item_list.append(to_team)
                                else:
                                    item_list.append("")

                                item_list.append(i['type'])

                                transaction_summary.extend(item_list)

                                if espn_transaction_id not in self.espn_trans_ids:
                                    self.DB.insert_list("RosterChanges", transaction_summary)
                                    if transaction['status'] == 'EXECUTED':
                                        if i['type'] != 'LINEUP':
                                            push_str = self.push_instance.string_from_list(
                                                [update_datetime, from_team, to_team, player_name, i['type']])
                                            push_list.extend(push_str)
                                        else:
                                            push_str = self.push_instance.string_from_list(
                                                [update_datetime, team_id, "From", from_position, " To", to_position,
                                                 player_name, i['type']])
                                            push_list.extend(push_str)

                                transaction_summary.clear()

                if len(push_list) > 0:
                    self.push_instance.push_list(push_list, "Transactions")
                    push_list.clear()

    def load_position_dict(self, use_pickle=True):
        position_dict = {}
        self.msg += "load_position_dict()\n\n"
        if use_pickle and path.exists("dict.pickle") and open("dict.pickle", "rb"):
            self.msg += "Load from pickle\n\n"
            pickle_in = open("dict.pickle", "rb")
            position_dict = pickle.load(pickle_in)
        else:
            self.msg += "Load from DB\n\n"
            c = self.DB.select("SELECT PositionID, Position from ESPNPositions")
            for t in c:
                position_dict[str(t[0])] = str(t[1])
        pickle_out = open("dict.pickle", "wb")
        pickle.dump(position_dict, pickle_out)
        pickle_out.close()
        return position_dict

    def populate_team_owners(self, leagueID):
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID)
        with urllib.request.urlopen(url_name) as url:
            json_object = json.loads(url.read().decode())

            # json_formatted = json.dumps(json_object, indent=2)
            for team in json_object['teams']:
                print(team)
                for owner in team['owners']:
                    insert_list = [owner, str(leagueID), str(team['id']),
                                   str(team['location']) + " " + team['nickname']]
                    self.DB.insert_list("ESPNTeamOwners", insert_list)

    def run_transactions(self, teams):
        for team in teams:
            self.get_transactions(team)

    def set_espn_default_league(self):
        leagueID = 0
        query = "select LeagueID from DefaultLeague"
        rows = self.DB.query(query)
        for row in rows:
            leagueID = row['LeagueID']
        return leagueID
