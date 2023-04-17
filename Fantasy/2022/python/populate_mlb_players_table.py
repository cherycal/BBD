__author__ = 'chance'
import sys
import time

sys.path.append('./modules')
import sqldb
import requests
import json
import pandas as pd
import statsapi

# My python class: sqldb.py
mode = "PROD"
if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')
# name = "Javier Assad"

def get_teams():

    request_string = f'https://statsapi.mlb.com/api/v1/teams'
    response = json.loads(requests.get(request_string).text)

    column_names = ["teamId","teamName","teamAbbr","teamLg","teamLgId","teamDivision","teamDivisionId"]

    entries = []

    for team in response['teams']:
        if team.get('sport'):
            #print(team['sport'])
            if team['sport'].get('id') == 16:
                #print(team)
                teamName = team['name']
                teamId = team['id']
                teamAbbr = team['abbreviation']
                teamLg = team['league']['name']
                teamLgId = team['league']['id']
                teamDivision = ""
                if team.get('division'):
                    teamDivision = team['division']['name']
                teamDivisionId = ""
                if  team.get('division'):
                    teamDivisionId = team['division']['id']
                entry = [teamId,teamName,teamAbbr,teamLg,teamLgId,teamDivision,teamDivisionId]
                print(entry)
                entries.append(entry)

    df = pd.DataFrame(entries, columns=column_names)

    table_name = "MLBTeams"
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

    return 0



def get_rosters():
    data = bdb.select_table("MLBTeams")

    for dict_ in data['dicts']:
        print(dict_['teamId'])
        teamName = dict_['teamName']
        teamId = dict_['teamId']
        request_string = f'https://statsapi.mlb.com/api/v1/teams/{teamId}/roster'
        response = json.loads(requests.get(request_string).text)
        #print(response)

        if response.get('roster'):
            people = response['roster']

            # column_names = ["mlbid", "fullName", "firstName", "lastName", "birthDate", "currentAge", "birthCountry",
            #                 "active", "primaryPosition", "bats",
            #                 "throws", "draftYear"]
            #
            # entries = []

            for player in people:
                mlbid = player['person']['id']
                fullName = player['person']['fullName']
                position = player['position']['abbreviation']
                entry = [teamId, teamName, mlbid, fullName, position]
                print(entry)

    return 0

def find_player_by_name():
    players = statsapi.lookup_player('Bracho,')
    for player in players:
        print(f'id:{player["id"]}, fullName:{player["fullName"]}')
    return 0


def find_players_by_ids(string):
    request_string = f'https://statsapi.mlb.com/api/v1/people?personIds={string}'
    response = json.loads(requests.get(request_string).text)
    people = response.get('people')

    column_names = ["mlbid", "fullName", "firstName", "lastName", "birthDate", "currentAge", "birthCountry", "active",
                    "primaryPosition", "bats",
                    "throws", "draftYear"]

    entries = []

    if people:
        for player in people:
            #print(player)
            mlbid = player['id']
            fullName = player['fullName']
            firstName = player['firstName']
            lastName = player.get('lastName')
            birthDate = player.get('birthDate')
            currentAge = player.get('currentAge')
            birthCountry = player.get('birthCountry')
            active = player['active']
            primaryPosition = player['primaryPosition']['abbreviation']
            bats = "NA"
            if player.get('batSide'):
                bats = player.get('batSide').get('description')
            throws = "NA"
            if player.get('pitchHand'):
                throws = player.get('pitchHand').get('description')
            draftYear = player.get('draftYear')

            entry = [mlbid, fullName, firstName, lastName, birthDate, currentAge, birthCountry, active, primaryPosition,
                     bats,
                     throws, draftYear]
            entries.append(entry)

        print(f'{entries}')
        df = pd.DataFrame(entries, columns=column_names)

        table_name = "MLBPlayers"
        df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

            #print(f'{mlbid},{fullName},{birthDate},{currentAge},{birthCountry},{active},{primaryPosition},{bats},{throws},{draftYear}')
    return 0


def create_number_string(start, step):
    end = start + step
    string = ""
    for i in range(start,end,1):
        string += str(i)
        if i < end - 1:
            string += ","
    return string

def create_multiple_number_strings():
    start = 800000
    step = 800
    end = 808000
    current = start
    while current < end:
        ids = create_number_string(current, step)
        find_players_by_ids(ids)
        print(f'Ran from {current} to {current + step - 1}')
        time.sleep(5)
        current += step

def populate_players():

    # Deprecated, has some older players
    # https://appac.github.io/mlb-data-api-docs/
    # http://lookup-service-prod.mlb.com/json/named.search_player_all.bam?sport_code='mlb'&active_sw='Y'&name_part='cespedes%25'

    # Prior years ...
    # https://statsapi.mlb.com/api/v1/sports/1/players?fields=people,firstLastName,lastName,nameSlug,birthCountry&season=2021

    request_string = f'https://statsapi.mlb.com/api/v1/people/changes?updatedSince=2020-04-01'
    sports = f'https://statsapi.mlb.com/api/v1/sports/1/players'
    response = json.loads(requests.get(request_string).text)

    data = bdb.select_table("ACheck_ID")
    people = response['people']

    column_names = ["mlbid", "fullName", "firstName","lastName","birthDate", "currentAge", "birthCountry", "active", "primaryPosition", "bats",
                    "throws", "draftYear"]

    entries = []

    for player in people:
        mlbid = player['id']
        fullName = player['fullName']
        firstName = player['firstName']
        lastName = player.get('lastName')
        birthDate = player.get('birthDate')
        currentAge = player.get('currentAge')
        birthCountry = player.get('birthCountry')
        active = player['active']
        primaryPosition = player['primaryPosition']['abbreviation']
        bats = "NA"
        if player.get('batSide'):
            bats = player.get('batSide').get('description')
        throws = "NA"
        if player.get('pitchHand'):
            throws = player.get('pitchHand').get('description')
        draftYear = player.get('draftYear')

        entry = [mlbid, fullName, firstName,lastName,birthDate, currentAge, birthCountry, active, primaryPosition, bats,
                    throws, draftYear]
        entries.append(entry)

        print(f'{mlbid},{fullName},{birthDate},{currentAge},{birthCountry},{active},{primaryPosition},{bats},{throws},{draftYear}')

    df = pd.DataFrame(entries, columns=column_names)

    table_name = "MLBPlayers"
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

    return 0



# names = list()
# for dict_ in data['dicts']:
#     name = dict_['name']
#     if name not in names:
#         names.append(name)
# print(names)


def main():
    create_multiple_number_strings()
    #ids = create_number_string(677570)
    #find_players_by_ids(ids)
    #find_player_by_name()


    #get_teams()
    #get_rosters()
    #populate_players()
    bdb.close()
    print("Done")


if __name__ == "__main__":
    main()
