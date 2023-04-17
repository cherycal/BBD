__author__ = 'chance'
import sys
sys.path.append('./modules')
import sqldb
import requests
import json
import pandas as pd

# My python class: sqldb.py
mode = "PROD"
if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')
# name = "Javier Assad"

request_string = f'https://statsapi.mlb.com/api/v1/people/changes?updatedSince=2023-01-01'
response = json.loads(requests.get(request_string).text)
people = response['people']


#data = bdb.select_table("ACheck_ID")

column_names = ["mlbid", "fullName", "firstName","lastName","birthDate", "currentAge", "birthCountry", "active", "primaryPosition", "bats",
                "throws", "draftYear"]

entries = []

for player in people:
    mlbid = player['id']
    fullName = player['fullName']
    firstName = player.get('firstName')
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
print(df)

table_name = "MLBPlayers"
# df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

# names = list()
# for dict_ in data['dicts']:
#     name = dict_['name']
#     if name not in names:
#         names.append(name)
# print(names)

bdb.close()
