__author__ = 'chance'

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta

sys.path.append('./modules')
import sqldb, tools, fantasy
import pickle
import os.path
from os import path
import push
import time
import inspect
import pycurl
import certifi
import io
from io import BytesIO


def get_default_position(positionID):
    switcher = {
        1: "SP",
        2: "C",
        3: "1B",
        4: "2B",
        5: "3B",
        6: "SS",
        7: "LF",
        8: "CF",
        9: "RF",
        10: "DH",
        11: "RP",
    }
    return switcher.get(positionID, "NA")


def print_calling_function():
    print('\n')
    print("Printing calling information (fantasy.py)")
    print("#############################")
    print(str(inspect.stack()[-2].filename) + ", " + str(inspect.stack()[-2].function) +
          ", " + str(inspect.stack()[-2].lineno))
    print(str(inspect.stack()[1].filename) + ", " + str(inspect.stack()[1].function) +
          ", " + str(inspect.stack()[1].lineno))
    print(str(inspect.stack()[-1].filename) + ", " + str(inspect.stack()[-1].function) +
          ", " + str(inspect.stack()[-1].lineno))
    print("#############################")
    return


def get_time():
    timedict = {}
    now = datetime.now()  # current date and time
    timedict['datetime'] = now.strftime("%Y%m%d%H%M%S")
    timedict['date_time'] = now.strftime("%Y%m%d-%H%M%S")
    timedict['date8'] = now.strftime("%Y%m%d")
    return timedict


class Fantasy(object):

    def __init__(self):
        self.timedict = {}
        print("Initializing Fantasy Object from " + str(inspect.stack()[-1].filename))
        self.push_msg = ""
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
        self.MLBTeamName = self.set_espn_MLB_team_map()
        self.ownerTeam = self.set_owner_team_map()
        self.position2 = self.set_espn_position_map()
        self.position = self.load_position_dict()
        self.player, self.player_team = self.set_espn_player()
        # self.espn_player_json = self.set_espn_player_json()
        self.espn_trans_ids = self.get_espn_trans_ids()
        self.leagues = self.get_leagues()
        self.active_leagues = self.get_active_leagues()
        self.default_league = self.set_espn_default_league()
        self.str = ""
        self.db_player_status = {}
        self.current_player_status = {}
        self.player_insert_list = list()
        self.players = {}
        self.push_msg_list = list()
        self.transactions = {}
        self.player_data_json = object()
        self.roster_lock_time = self.set_roster_lock_time()

    ##########################################################################

    class Player:
        def __init__(self, espnid_):
            now = datetime.now()  # current date and time
            self.date = now.strftime("%Y%m%d")
            self.time = now.strftime("%Y%m%d-%H%M%S")
            self.espnid = espnid_
            self.name = "NA"
            self.injuryStatus = "NA"
            self.throws = "NA"
            self.bats = "NA"
            self.primaryPosition = "NA"
            self.eligiblePositions = "NA"
            self.mlbTeam = "NA"
            self.auctionValueAverage = 0.0
            self.auctionValueAverageChange = 0.0
            self.averageDraftPosition = 0.0
            self.percentOwned = 0.0
            self.percentStarted = 0.0
            self.nextStart = "NA"
            self.status = "NA"

        def get_player_data_fields(self):
            fields = list()
            fields.append(self.get_date())
            fields.append(self.get_time())
            fields.append(self.get_espnid())
            fields.append(self.get_name())
            fields.append(self.get_injuryStatus())
            fields.append(self.get_throws())
            fields.append(self.get_bats())
            fields.append(self.get_primaryPosition())
            fields.append(self.get_eligiblePositions())
            fields.append(self.get_mlbTeam())
            fields.append(self.get_auctionValueAverage())
            fields.append(self.get_auctionValueAverageChange())
            fields.append(self.get_averageDraftPosition())
            fields.append(self.get_percentOwned())
            fields.append(self.get_percentStarted())
            fields.append(self.get_nextStartId())
            fields.append(self.get_status())
            return tuple(fields)

        def get_espnid(self):
            return self.espnid

        def get_date(self):
            now = datetime.now()  # current date and time
            self.date = now.strftime("%Y%m%d")
            return self.date

        def get_time(self):
            now = datetime.now()  # current date and time
            self.time = now.strftime("%Y%m%d-%H%M%S")
            return self.time

        def get_name(self):
            return self.name

        def get_injuryStatus(self):
            return self.injuryStatus

        def get_status(self):
            return self.status

        def get_throws(self):
            return self.throws

        def get_primaryPosition(self):
            return self.primaryPosition

        def get_bats(self):
            return self.bats

        def get_eligiblePositions(self):
            return self.eligiblePositions

        def get_mlbTeam(self):
            return self.mlbTeam

        def get_auctionValueAverage(self):
            return self.auctionValueAverage

        def get_auctionValueAverageChange(self):
            return self.auctionValueAverageChange

        def get_percentStarted(self):
            return self.percentStarted

        def get_percentOwned(self):
            return self.percentOwned

        def get_nextStartId(self):
            return self.nextStart

        def get_averageDraftPosition(self):
            return self.averageDraftPosition

        def set_name(self, name_):
            self.name = name_

        def set_start(self, start_):
            self.nextStart = start_

        def set_injuryStatus(self, injuryStatus_):
            self.injuryStatus = injuryStatus_

        def set_throws(self, throws_):
            self.throws = throws_

        def set_bats(self, bats_):
            self.bats = bats_

        def set_mlbTeam(self, mlbTeam_):
            self.mlbTeam = mlbTeam_

        def set_primaryPosition(self, primaryPosition_):
            self.primaryPosition = primaryPosition_

        def set_eligiblePositions(self, eligiblePositions_):
            self.eligiblePositions = eligiblePositions_

        def set_auctionValueAverage(self, auctionValueAverage_):
            self.auctionValueAverage = auctionValueAverage_

        def set_auctionValueAverageChange(self, auctionValueAverageChange_):
            self.auctionValueAverageChange = auctionValueAverageChange_

        def set_averageDraftPosition(self, averageDraftPosition_):
            self.averageDraftPosition = averageDraftPosition_

        def set_percentOwned(self, percentOwned_):
            self.percentOwned = percentOwned_

        def set_percentStarted(self, percentStarted_):
            self.percentStarted = percentStarted_

        def set_status(self, status_):
            self.status = status_

        def print_attrs(self):
            print(vars(self).keys())
            print(vars(self).values())

        def keys(self):
            return vars(self).keys()

        def values(self):
            return vars(self).values()

    ###########################################

    class Transaction:
        def __init__(self, espntransid_):
            self.espntransid = espntransid_
            self.update_date = 0
            self.update_time = ""
            self.update_time_hhmmss = 0
            self.fantasy_team_name = ""
            self.status = ""
            self.type = ""
            self.transid = ""
            self.from_position = ""
            self.from_team = ""
            self.player_name = ""
            self.to_position = ""
            self.to_team = ""
            self.leg_type = ""
            self.espnid = ""
            self.leagueID = ""

        def set_leagueID(self, leagueID):
            self.leagueID = leagueID

        def get_leagueID(self):
            return self.leagueID

        def get_espnid(self):
            return self.espnid

        def set_espnid(self, espnid):
            self.espnid = espnid

        def get_transaction_fields(self):
            fields = list()
            fields.append(self.get_espntransid())
            fields.append(self.get_update_date())
            fields.append(self.get_update_time())
            fields.append(self.get_fantasy_team_name())
            fields.append(self.get_status())
            fields.append(self.get_type())
            fields.append(self.get_transid())
            fields.append(self.get_from_position())
            fields.append(self.get_from_team())
            fields.append(self.get_player_name())
            fields.append(self.get_to_position())
            fields.append(self.get_to_team())
            fields.append(self.get_leg_type())
            return tuple(fields)

        def set_leg_type(self, leg_type):
            self.leg_type = leg_type

        def get_leg_type(self):
            return self.leg_type

        def set_to_team(self, to_team):
            self.to_team = to_team

        def get_to_team(self):
            return self.to_team

        def set_to_position(self, to_position):
            self.to_position = to_position

        def get_to_position(self):
            return self.to_position

        def set_player_name(self, player_name):
            self.player_name = player_name

        def get_player_name(self):
            return self.player_name

        def set_from_team(self, from_team):
            self.from_team = from_team

        def get_from_team(self):
            return self.from_team

        def set_from_position(self, from_position):
            self.from_position = from_position

        def get_from_position(self):
            return self.from_position

        def set_transid(self, transid):
            self.transid = transid

        def get_transid(self):
            return self.transid

        def set_type(self, type_):
            self.type = type_

        def get_type(self):
            return self.type

        def set_status(self, status):
            self.status = status

        def get_status(self):
            return self.status

        def set_fantasy_team_name(self, name):
            self.fantasy_team_name = name

        def get_fantasy_team_name(self):
            return self.fantasy_team_name

        def set_update_time(self, update_time="", update_time_hhmmss=""):
            now = datetime.now()  # current date and time
            if update_time == "":
                update_time = now.strftime("%Y%m%d-%H%M%S.%f")
                update_time_hhmmss = now.strftime("%H%M%S")
            self.update_time = update_time
            self.update_time_hhmmss = update_time_hhmmss

        def get_update_time_hhmmss(self):
            return self.update_time_hhmmss

        def get_update_time(self):
            return self.update_time

        def get_espntransid(self):
            return self.espntransid

        def set_update_date(self, update_date=""):
            if update_date == "":
                now = datetime.now()  # current date and time
                update_date = now.strftime("%Y%m%d")
            self.update_date = update_date

        def get_update_date(self):
            return self.update_date

        def print_attrs(self):
            print(vars(self).keys())
            print(vars(self).values())

        def keys(self):
            return vars(self).keys()

        def values(self):
            return vars(self).values()

    ###########################################

    def get_roster_lock_time(self):
        return self.roster_lock_time

    def set_roster_lock_time(self):
        url_name = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

        with urllib.request.urlopen(url_name) as url:
            data = json.loads(url.read().decode())

            for i in data['events']:
                date_str = str(i['date'])
                date_str = date_str.replace("T", " ")
                date_str = date_str.replace("Z", "")
                datetime_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                datetime_object = datetime_object - timedelta(hours=7)
                lock_time = int(datetime.strftime(datetime_object, '%H%M%S'))
                self.roster_lock_time = lock_time
                return lock_time


    def get_time(self):
        now = datetime.now()  # current date and time
        self.timedict[datetime] = int(now.strftime("%Y%m%d%H%M%S"))
        self.timedict[date_time] = int(now.strftime("%Y%m%d%H%M%S"))
        self.timedict[date8] = int(now.strftime("%Y%m%d"))
        return self.timedict

    def get_player_object(self, id_):
        print_calling_function()
        return self.players[str(id_)]

    def team_name(self, proTeamID):
        team = "NA"
        if str(proTeamID) in self.MLBTeamName:
            team = self.MLBTeamName[str(proTeamID)]
        return team

    def get_position(self, positionID):
        pos = "NA"
        if str(positionID) in self.position2:
            pos = self.position2[str(positionID)]
        return pos

    def league_standings(self):
        leagueID = self.default_league
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID) + "?view=standings"
        print("league_standings: " + url_name)
        with urllib.request.urlopen(url_name) as url:
            json_object = json.loads(url.read().decode())
            # json_formatted = json.dumps(json_object, indent=2)
            # print(json_formatted)
        return json_object

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

    def set_espn_MLB_team_map(self):
        teamName = {}
        query = "select MLBTeamID, MLBTeam from ESPNMLBTeams"
        rows = self.DB.query(query)
        for row in rows:
            teamName[str(row['MLBTeamID'])] = str(row['MLBTeam'])
        return teamName

    def set_espn_player(self):
        player = {}
        player_team = {}
        query = "select espnid, name, mlbTeam from PlayerDataCurrent"
        rows = self.DB.query(query)
        for row in rows:
            player[str(row['espnid'])] = str(row['name'])
            player_team[str(row['espnid'])] = str(row['mlbTeam'])
        return player, player_team

    def set_espn_player_json(self):
        print_calling_function()
        leagueID = self.default_league
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID) + "?view=kona_playercard"
        print("set_espn_player_json: " + url_name)
        with urllib.request.urlopen(url_name) as url:
            json_object = json.loads(url.read().decode())
            # json_formatted = json.dumps(json_object, indent=2)
        return json_object

    def get_db_player_status(self):
        return self.db_player_status

    def get_db_player_info(self):
        print_calling_function()
        player_status = {}
        rows = self.DB.query("select Date, espnid, injuryStatus, status, nextStartID from PlayerDataCurrent")
        for row in rows:
            key = str(row['espnid'])
            # key = str(row['Date']) + ':' + str(row['espnid'])
            player_status[key] = {}
            if 'injuryStatus' in player_status[key]:
                player_status[key]['injuryStatus'] = str(row['injuryStatus'])
            else:
                player_status[key]['injuryStatus'] = {}
                player_status[key]['injuryStatus'] = str(row['injuryStatus'])
            if 'status' in player_status[key]:
                player_status[key]['status'] = str(row['status'])
            else:
                player_status[key]['status'] = {}
                player_status[key]['status'] = str(row['status'])
            if 'nextStartID' in player_status[key]:
                player_status[key]['nextStartID'] = str(row['nextStartID'])
            else:
                player_status[key]['nextStartID'] = {}
                player_status[key]['nextStartID'] = str(row['nextStartID'])

        self.db_player_status = player_status.copy()

    def refresh_rosters(self):
        pos_map = self.set_espn_position_map()
        now = datetime.now()
        update_date = now.strftime("%Y%m%d-%H%M%S")
        insert_list = list()
        for league in self.active_leagues:
            addr = "https://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(league)  + \
                "?view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions&" + \
            "view=mPositionalRatings&view=mRoster&view=mSettings&view=mTeam&view=modular&view=mNav"
            print(addr)

            with urllib.request.urlopen(addr) as url:
                data = json.loads(url.read().decode())
                for i in data['schedule']:
                    for j in i['teams']:
                        team_id = str(j['teamId'])
                        team_name = self.teamName[str(league)][team_id]
                        for k in j['rosterForCurrentScoringPeriod']['entries']:
                            league = str(league)
                            pos = str(pos_map[str(k['lineupSlotId'])])
                            espn_id = str(k['playerId'])
                            player_full_name = k['playerPoolEntry']['player']['fullName']
                            entry = (player_full_name, team_name, league, espn_id, pos, update_date)
                            print(entry)
                            insert_list.append(entry)


        count = len(insert_list)
        print(count)
        if count > 1100:
            command = "Delete from Rosters"
            self.DB.delete(command)
            print("\nDelete Rosters worked\n")
            self.DB.insert_many("Rosters", insert_list)
            print("\nInsert Rosters worked\n")

    # def refresh_rosters_table(self):
    #     now = datetime.now()
    #     date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
    #     update_date = now.strftime("%Y%m%d")
    #     insert_list_many = list()
    #     MINIMUM = 25 * 10 * len(self.active_leagues)
    #     pos_map = self.set_espn_position_map()
    #     for league in self.active_leagues:
    #         addr = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + str(
    #             league) + "?view=mRoster&view=mTeam&view=modular&view=mNav"
    #         print(addr)
    #
    #         with urllib.request.urlopen(addr) as url:
    #             data = json.loads(url.read().decode())
    #
    #         for team in data['teams']:
    #             team_name = team['location'] + " " + team['nickname']
    #             if 'roster' in team:
    #                 for player in team['roster']['entries']:
    #                     player_full_name = player['playerPoolEntry']['player']['fullName']
    #                     pos = str(pos_map[str(player['lineupSlotId'])])
    #                     espn_id = player['playerPoolEntry']['player']['id']
    #                     entry = (player_full_name, team_name, str(league), str(espn_id), pos, update_date)
    #                     print(entry)
    #                     insert_list_many.append(entry)
    #
    #
    #     if len(insert_list_many) > MINIMUM:
    #         tries = 0
    #         TRIES_BEFORE_QUITTING = 3
    #         SLEEP = 5
    #         passed = 0
    #         command = ""
    #         while tries < TRIES_BEFORE_QUITTING:
    #             tries += 1
    #             try:
    #                 command = "Delete from Rosters"
    #                 self.DB.delete(command)
    #                 print("\nDelete Rosters worked\n")
    #                 passed = 1
    #                 break
    #             except Exception as ex:
    #                 self.push_instance.push(
    #                     "DATABASE ERROR Delete Rosters- try " + str(tries) + " at " + str(date_time),
    #                     command + ": " + str(ex))
    #             time.sleep(SLEEP)
    #
    #         if not passed:
    #             self.push_instance.push("DATABASE ERROR", command)
    #
    #         tries = 0
    #         passed = 0
    #
    #         while tries < TRIES_BEFORE_QUITTING:
    #             tries += 1
    #             try:
    #                 self.DB.insert_many("Rosters", insert_list_many)
    #                 print("\ninsert Rosters worked\n")
    #                 passed = 1
    #                 break
    #             except Exception as ex:
    #                 print("Exception:")
    #                 print(ex)
    #                 self.push_instance.push("DATABASE ERROR - try " + str(tries) + " at " + str(date_time),
    #                                         "Insert Rosters" + ": " + str(ex))
    #             time.sleep(SLEEP)
    #
    #         if not passed:
    #             self.push_instance.push("DATABASE ERROR", "insert PlayerDataCurrent, espn_player_info")
    #         # else:
    #         #     self.push_instance.push("REFRESH ROSTERS SUCCEEDS", "insert PlayerDataCurrent, espn_player_info")
    #
    #     return

    def get_current_player_status(self):
        return self.current_player_status

    def get_espn_player_info(self):
        print_calling_function()
        player_status = {}
        self.get_player_data_json()
        espn_player_json = self.player_data_json
        insert_many_list = list()
        for player in espn_player_json['players']:
            player_obj = self.Player(player['id'])
            if 'fullName' in player['player']:
                player_obj.set_name(player['player']['fullName'])
            if 'injuryStatus' in player['player']:
                player_obj.set_injuryStatus(player['player']['injuryStatus'])
            if 'status' in player:
                player_obj.set_status(player['status'])
            # noinspection SpellCheckingInspection
            if 'defaultPositionId' in player['player']:
                player_obj.set_primaryPosition(get_default_position(player['player']['defaultPositionId']))
            if 'eligibleSlots' in player['player']:
                eligible_slots = player['player']['eligibleSlots']
                position_list = []
                for position_id in eligible_slots:
                    if position_id < 16 and position_id != 12:
                        position_list.append(self.get_position(position_id))
                position_string = str(position_list)[1:-1]
                player_obj.set_eligiblePositions(position_string)
            if 'laterality' in player['player']:
                player_obj.set_throws(player['player']['laterality'])
            if 'stance' in player['player']:
                player_obj.set_bats(player['player']['stance'])
            if 'nextStartExternalId' in player['player']:
                player_obj.set_start(player['player']['nextStartExternalId'])
            if 'proTeamId' in player['player']:
                player_obj.set_mlbTeam(self.team_name(player['player']['proTeamId']))
            if 'ownership' in player['player']:
                player_obj.set_auctionValueAverage(round(player['player']['ownership']['auctionValueAverage'], 2))
                player_obj.set_auctionValueAverageChange(
                    round(player['player']['ownership']['auctionValueAverageChange'], 2))
                player_obj.set_averageDraftPosition(round(player['player']['ownership']['auctionValueAverage'], 2))
                player_obj.set_percentOwned(round(player['player']['ownership']['percentOwned'], 2))
                player_obj.set_percentStarted(round(player['player']['ownership']['percentStarted'], 2))

            if int(player_obj.percentOwned) >= 0:
                insert_list = list()
                insert_list.extend(player_obj.values())
                self.player_insert_list.append(insert_list)
                insert_many_list.append(tuple(insert_list))

            key = str(player_obj.get_espnid())
            player_status[key] = {}
            if 'injuryStatus' in player_status[key]:
                player_status[key]['injuryStatus'] = str(player_obj.get_injuryStatus())
            else:
                player_status[key]['injuryStatus'] = {}
                player_status[key]['injuryStatus'] = str(player_obj.get_injuryStatus())
            if 'status' in player_status[key]:
                player_status[key]['status'] = str(player_obj.get_status())
            else:
                player_status[key]['status'] = {}
                player_status[key]['status'] = str(player_obj.get_status())
            if 'nextStartID' in player_status[key]:
                player_status[key]['nextStartID'] = str(player_obj.get_nextStartId())
            else:
                player_status[key]['nextStartID'] = {}
                player_status[key]['nextStartID'] = str(player_obj.get_nextStartId())

            self.players[str(player['id'])] = player_obj

        self.current_player_status = player_status
        return insert_many_list

    def get_player_data_json(self):
        print_calling_function()
        leagueID = self.default_league
        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID) + "?view=kona_playercard"
        headers = ['authority: fantasy.espn.com',
                   'accept: application/json',
                   'x-fantasy-source: kona',
                   'x-fantasy-filter: {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS","ONTEAM"]},'
                   '"filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]}}}']
        print("get_player_data_json: " + url_name)
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url_name)
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.CAINFO, certifi.where())
        c.perform()
        c.close()

        data = buffer.getvalue()

        self.player_data_json = json.loads(data)
        # json_formatted = json.dumps(self.player_data_json, indent=2)

        # print(json_formatted)

    def get_player_info_changes(self):
        print_calling_function()
        now = datetime.now()  # current date and time
        date_time = now.strftime("%Y%m%d-%H%M%S")
        out_date = now.strftime("%Y%m%d")
        for i in self.get_current_player_status():
            if i in self.get_db_player_status():
                for j in self.get_current_player_status()[i]:
                    if self.get_current_player_status()[i][j] != self.get_db_player_status()[i][j]:
                        espnid = i
                        name = str(self.get_player_object(i).name)
                        set_attr = j
                        old = self.get_db_player_status()[i][j]
                        new = self.get_current_player_status()[i][j]
                        where_attr = 'espnid'
                        if set_attr != "nextStartID":
                            self.push_msg_list.append(
                                tools.string_from_list([name, set_attr, 'old:', old, 'new:', new]))
                        self.DB.update_list("ESPNPlayerDataCurrent", set_attr, where_attr, (new, espnid))
                        self.DB.update_list("ESPNPlayerDataCurrent", "Date", where_attr, (out_date, espnid))
                        self.DB.update_list("ESPNPlayerDataCurrent", "UpdateTime", where_attr, (date_time, espnid))
                        self.DB.insert_list("ESPNStatusChanges", [out_date, date_time, espnid, set_attr, old, new])
            else:
                print("No corresponding data in ESPNPlayerDataCurrent for " + i)
                # Insert into PlayerDataCurrent
                insert_many_list = list()
                insert_many_list.append(self.players[str(i)].get_player_data_fields())
                self.DB.insert_many("ESPNPlayerDataCurrent", insert_many_list)

    def send_push_msg_list(self):
        if len(self.push_msg_list):
            self.push_instance.push_list(self.push_msg_list, "Status changes")
            self.push_msg_list.clear()
        return

    def set_espn_position_map(self):
        position = {}
        query = "select PositionID, Position from ESPNPositions"
        rows = self.DB.query(query)
        for row in rows:
            position[str(row['PositionID'])] = str(row['Position'])
        return position

    def get_espn_trans_ids(self):
        espn_trans_ids = {}
        query = "select distinct ESPNTransID from ESPNRosterChanges"
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
        query = "select distinct LeagueID from ESPNLeagues"
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

    def build_transactions(self, leagueID):

        url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
                   str(leagueID) + "?view=mTransactions2"
        print("build_transactions: " + url_name)

        with urllib.request.urlopen(url_name) as url:
            json_object = json.loads(url.read().decode())
            push_list = list()

            if 'transactions' in json_object:
                for transaction in json_object['transactions']:
                    espn_transaction_id = transaction['id']
                    seconds = int(transaction['proposedDate']) / 1000.000
                    sub_seconds = str(round(seconds - int(seconds), 3))[1:]
                    update_date = time.strftime("%Y%m%d", time.localtime(seconds))
                    update_time = time.strftime("%Y%m%d-%H%M%S", time.localtime(seconds))
                    update_time_hhmmss = time.strftime("%H%M%S", time.localtime(seconds))
                    update_time += str(sub_seconds)
                    team_name = self.teamName[str(leagueID)][str(transaction['teamId'])]

                    item_count = 0
                    if 'items' in transaction:
                        for i in transaction['items']:

                            trans_obj = self.Transaction(espn_transaction_id)
                            trans_obj.set_leagueID(leagueID)
                            trans_obj.set_update_date(update_date)
                            trans_obj.set_update_time(update_time, update_time_hhmmss)
                            trans_obj.set_fantasy_team_name(team_name)
                            trans_obj.set_status(transaction['status'])
                            trans_obj.set_leg_type(i['type'])

                            item_list = list()
                            item_count += 1

                            transaction_id = espn_transaction_id + str(item_count)
                            trans_obj.set_transid(transaction_id)
                            item_list.append(transaction_id)

                            from_position = ""
                            if int(i['fromLineupSlotId']) >= 0:
                                from_position = self.position[i['fromLineupSlotId']]
                            trans_obj.set_from_position(from_position)

                            from_team = ""
                            if i['fromTeamId'] > 0:
                                from_team = self.teamName[str(leagueID)][str(i['fromTeamId'])]
                            trans_obj.set_from_team(from_team)

                            player_name = ""
                            espnid = ""
                            if str(i['playerId']) in self.player:
                                player_name = self.player[str(i['playerId'])]
                                espnid = str(i['playerId'])
                                item_list.append(player_name)
                            else:
                                print("Missing playerID for " + str(i['playerId']) + "(" + str(i) + ")")
                            trans_obj.set_player_name(player_name)
                            trans_obj.set_espnid(espnid)

                            to_position = "B"
                            if int(i['toLineupSlotId']) >= 0:
                                to_position = self.position[i['toLineupSlotId']]
                                item_list.append(to_position)
                            trans_obj.set_to_position(to_position)

                            to_team = ""
                            if 'toTeamId' in i and i['toTeamId'] > 0:
                                to_team = self.teamName[str(leagueID)][str(i['toTeamId'])]
                                item_list.append(to_team)
                            trans_obj.set_to_team(to_team)

                            item_list.append(i['type'])
                            trans_obj.set_type(transaction['type'])

                            index = str(trans_obj.get_update_time()) + str(trans_obj.get_transid())

                            #print("In build_transactions, transaction at " + str(trans_obj.get_update_time_hhmmss()))
                            #print("Roster lock time is " + str(self.get_roster_lock_time()))
                            # espn_trans_ids from RosterChanges table ESPNTransID
                            if (espn_transaction_id not in self.espn_trans_ids) or \
                                    (int(trans_obj.get_update_time_hhmmss()) >= int(self.get_roster_lock_time())):
                                if transaction['status'] == 'EXECUTED':

                                    self.transactions[index] = trans_obj
                                    fields = trans_obj.get_transaction_fields()

                                    if (espn_transaction_id not in self.espn_trans_ids) and i['type'] != '':
                                        print("Build transactions insert ESPNRosterChanges fields:")
                                        print(fields)

                                        self.DB.insert_list("ESPNRosterChanges", fields)

                                        if trans_obj.get_type() != "FUTURE_ROSTER":
                                            push_str = \
                                                self.push_instance.string_from_list([update_time, team_name,
                                                                                     "from:", from_position, "to:",
                                                                                     to_position, from_team, to_team,
                                                                                     player_name, i['type']])
                                            print("Push String: " + push_str)
                                            push_list.append(push_str)

            if len(push_list) > 0:
                self.push_instance.push_list(push_list, "Transactions")
                push_list.clear()

                #                 if transaction['type'] != "FUTURE_ROSTER":
                #                     command = "update ROSTERS set Position = \"" + to_position + \
                #                               "\" where LeagueID = " + \
                #                               str(leagueID) + " and ESPNID = " + str(i['playerId'])
                #                     print("Build transactions update command:")
                #                     print(command)
                #                     # self.DB.update(command)
                #
                #                 if i['type'] == 'ADD':
                #                     insert_many_list = list()
                #                     entry = (player_name, to_team, str(leagueID),
                #                              str(i['playerId']), "B", str(update_date))
                #                     print("Build transactions Rosters insert command:")
                #                     print(entry)
                #                     insert_many_list.append(entry)
                #                     # self.DB.insert_many("Rosters", insert_many_list)
                #
                #                 if i['type'] == 'DROP':
                #                     delete_command = "DELETE from Rosters where ESPNID = " + \
                #                                      str(i['playerId']) + \
                #                                      " and LeagueID = " + str(leagueID)
                #                     delete_list.append(delete_command)
                #
                # for i in delete_list:
                #     print(i)
                #     # self.DB.delete(i)
                # delete_list.clear()

    def process_transactions(self):
        updates = list()
        adds = list()
        drops = list()
        for i in sorted(self.transactions.keys()):
            transaction = self.transactions[i]
            trans_type = transaction.get_leg_type()
            #player_name = transaction.get_player_name()
            # espn_trans_ids from RosterChanges table ESPNTransID
            print("Transaction inside process_transactions:")
            print(transaction.get_transaction_fields())
            if transaction.get_espntransid() not in self.espn_trans_ids or \
                    int(transaction.get_update_time_hhmmss()) >= int(self.get_roster_lock_time()):
                print("New transaction " + trans_type)
                print(transaction.get_transaction_fields())
                if trans_type == "LINEUP":
                    updates.append(transaction)
            if transaction.get_espntransid() not in self.espn_trans_ids:
                if trans_type == "ADD":
                    adds.append(transaction)
                if trans_type == "DROP":
                    drops.append(transaction)
            else:
                print("Old transaction at " + str(transaction.get_update_time_hhmmss()))
        print("process_transactions:")
        self.process_updates(updates)
        self.process_adds(adds)
        self.process_drops(drops)

    def process_updates(self, updates):
        print("Number of process_updates:")
        # takes a list of transaction objects
        print(len(updates))
        for transaction in updates:
            print("Update")
            to_position = transaction.get_to_position()
            leagueID = transaction.get_leagueID()
            print(transaction.get_to_position())
            espnid = transaction.get_espnid()
            print(transaction.get_espnid())
            self.DB.update_data("Update ESPNRosters set Position = ? where ESPNID = ? and LeagueID = ?",
                           (to_position, espnid, leagueID))

    def process_adds(self, adds):
        print("Number of process_adds:")
        # takes a list of transaction objects
        print(len(adds))
        #entry = list()
        for transaction in adds:
            print("Add")
            player_name = transaction.get_player_name()
            to_team = transaction.get_to_team()
            leagueID = transaction.get_leagueID()
            espnid = str(transaction.get_espnid())
            to_position = "B"
            update_time = transaction.get_update_time()
            # insert_many_list = list()
            entry = [player_name, to_team, leagueID,
                          espnid, to_position, update_time]
            print("Build transactions Rosters insert command:")
            print(entry)
            self.DB.insert_list("ESPNRosters", entry)

    def process_drops(self, drops):
        print("Number of process_drops:")
        print(len(drops))
        for transaction in drops:
            leagueID = transaction.get_leagueID()
            espnid = str(transaction.get_espnid())
            command = 'DELETE FROM ESPNRosters WHERE leagueID =? and ESPNID = ?'
            params = (leagueID, espnid,)
            self.DB.delete_item(command, params)

    # def get_transactions(self, leagueID):
    #     print_calling_function()
    #     url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/" + \
    #                str(leagueID) + "?view=mTransactions2"
    #     print("get_transactions: " + url_name)
    #
    #     with urllib.request.urlopen(url_name) as url:
    #         json_object = json.loads(url.read().decode())
    #         push_list = list()
    #         transaction_base = list()
    #         transaction_summary = list()
    #
    #         if 'transactions' in json_object:
    #             for transaction in json_object['transactions']:
    #                 transaction_base.clear()
    #                 transaction_summary.clear()
    #                 espn_transaction_id = transaction['id']
    #                 transaction_base.append(espn_transaction_id)
    #
    #                 seconds = int(transaction['proposedDate']) / 1000.000
    #                 update_date = time.strftime("%Y%m%d", time.localtime(seconds))
    #                 transaction_base.append(update_date)
    #                 update_time = time.strftime("%H%M%S", time.localtime(seconds))
    #                 transaction_base.append(update_time)
    #                 update_datetime = time.strftime("%Y%m%d%H%M%S", time.localtime(seconds))
    #
    #                 team_id = self.teamName[str(leagueID)][str(transaction['teamId'])]
    #                 transaction_base.append(team_id)
    #
    #                 if 'status' in transaction:
    #                     transaction_base.append(transaction['status'])
    #                 else:
    #                     transaction_base.append("")
    #                 transaction_base.append(transaction['type'])
    #
    #                 insert_list = list()
    #                 delete_list = list()
    #                 if 'transactions' in json_object:
    #                     item_count = 0
    #                     if 'items' in transaction:
    #                         for i in transaction['items']:
    #                             transaction_summary.extend(transaction_base)
    #                             item_list = list()
    #                             item_count += 1
    #
    #                             transaction_id = espn_transaction_id + str(item_count)
    #                             item_list.append(transaction_id)
    #
    #                             from_position = ""
    #                             if int(i['fromLineupSlotId']) > 0:
    #                                 from_position = self.position[i['fromLineupSlotId']]
    #                                 item_list.append(from_position)
    #                             else:
    #                                 item_list.append("")
    #
    #                             from_team = ""
    #                             if i['fromTeamId'] > 0:
    #                                 from_team = self.teamName[str(leagueID)][str(i['fromTeamId'])]
    #                                 item_list.append(from_team)
    #                             else:
    #                                 item_list.append("")
    #
    #                             if str(i['playerId']) in self.player:
    #                                 player_name = self.player[str(i['playerId'])]
    #                                 item_list.append(player_name)
    #                             else:
    #                                 print("Missing playerID for " + str(i['playerId']) + "(" + str(i) + ")")
    #                                 item_list.append("????")
    #
    #                             to_position = ""
    #                             if int(i['toLineupSlotId']) > 0:
    #                                 to_position = self.position[i['toLineupSlotId']]
    #                                 item_list.append(to_position)
    #                             else:
    #                                 item_list.append("")
    #
    #                             to_team = ""
    #                             if 'toTeamId' in i and i['toTeamId'] > 0:
    #                                 to_team = self.teamName[str(leagueID)][str(i['toTeamId'])]
    #                                 item_list.append(to_team)
    #                             else:
    #                                 item_list.append("")
    #
    #                             if 'type' in i:
    #                                 item_list.append(i['type'])
    #                             else:
    #                                 item_list.append("No type found ( run_transactions )")
    #                                 exit(-1)
    #
    #                             transaction_summary.extend(item_list)
    #
    #                             if espn_transaction_id not in self.espn_trans_ids:
    #                                 if transaction['status'] == 'EXECUTED':
    #                                     print("Transaction summary:")
    #                                     print(transaction_summary)
    #                                     self.DB.insert_list("RosterChanges", transaction_summary)
    #                                     if i['type'] != '':
    #                                         push_str = \
    #                                             self.push_instance.string_from_list([update_datetime, team_id,
    #                                                                                  "from:", from_position, "to:",
    #                                                                                  to_position, from_team, to_team,
    #                                                                                  player_name, i['type']])
    #                                         print("Push String: " + push_str)
    #                                         push_list.append(push_str)
    #                                     if transaction['type'] != "FUTURE_ROSTER":
    #                                         command = "update ROSTERS set Position = \"" + to_position + \
    #                                                   "\" where LeagueID = " + \
    #                                                   str(leagueID) + " and ESPNID = " + str(i['playerId'])
    #                                         print(command)
    #                                         self.DB.update(command)
    #                                     if i['type'] == 'ADD':
    #                                         insert_many_list = list()
    #                                         # insert_many_list.append(self.players[str(i)].get_player_data_fields())
    #                                         entry = (player_name, to_team, str(leagueID),
    #                                                  str(i['playerId']), "B", str(update_date))
    #                                         insert_many_list.append(entry)
    #                                         self.DB.insert_many("Rosters", insert_many_list)
    #                                         # command = "INSERT INTO Rosters(Player, Team, " \
    #                                         #           "LeagueID, ESPNID, Position, UpdateDate ) VALUES (\"" + \
    #                                         #           player_name + \
    #                                         #           "\" ,\"" + to_team + "\"," + str(leagueID) + "," + \
    #                                         #           str(i['playerId']) + ",'B'" + str(update_date) + ")"
    #                                         # insert_list.append(command)
    #                                     if i['type'] == 'DROP':
    #                                         delete_command = "DELETE from Rosters where ESPNID = " + str(
    #                                             i['playerId']) + \
    #                                                          " and LeagueID = " + str(leagueID)
    #                                         delete_list.append(delete_command)
    #
    #                                     # else:
    #                                     #     push_str = self.push_instance.string_from_list(
    #                                     #         [update_datetime, team_id, "From", from_position, " To", to_position,
    #                                     #          player_name, i['type']])
    #                                     #     push_list.extend(push_str)
    #
    #                             transaction_summary.clear()
    #                 # for i in insert_list:
    #                 #     self.DB.insert(i)
    #                 for i in delete_list:
    #                     self.DB.delete(i)
    #                 insert_list.clear()
    #                 delete_list.clear()
    #
    #             if len(push_list) > 0:
    #                 self.push_instance.push_list(push_list, "Transactions")
    #                 push_list.clear()

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
        print("populate_team_owners: " + url_name)
        with urllib.request.urlopen(url_name) as url:
            json_object = json.loads(url.read().decode())

            # json_formatted = json.dumps(json_object, indent=2)
            for team in json_object['teams']:
                print("Team:")
                print(team)
                for owner in team['owners']:
                    insert_list = [owner, str(leagueID), str(team['id']),
                                   str(team['location']) + " " + team['nickname']]
                    self.DB.insert_list("ESPNTeamOwners", insert_list)

    def run_transactions(self, teams=0):
        print_calling_function()
        if not teams:
            teams = self.get_active_leagues()
        self.espn_trans_ids = self.get_espn_trans_ids()
        for team in teams:
            self.build_transactions(team)
            # self.get_transactions(team)
        # print("Process transactions:")
        # time.sleep(1)
        # self.process_transactions()
        # time.sleep(1)

    def set_espn_default_league(self):
        leagueID = 0
        query = "select LeagueID from ESPNDefaultLeague"
        rows = self.DB.query(query)
        for row in rows:
            leagueID = row['LeagueID']
        return leagueID
