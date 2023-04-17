import sys

import pandas as pd
import requests

sys.path.append('./modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()


def main():
    #  url = 'https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?limit=18000'
    url = 'https://sports.core.api.espn.com/v3/sports/baseball/mlb/athletes?limit=100000'
    jsonData = requests.get(url).json()

    players = pd.DataFrame(jsonData['items'])

    bats = players['bats'].values.tolist()
    bats2 = list()
    for i in bats:
        bats2.append(i) if not isinstance(i, float) else bats2.append(
            {'type': 'RIGHT', 'abbreviation': 'R', 'displayValue': 'Right'})
    bats = bats2
    bats = pd.DataFrame.from_dict(bats)
    bats = bats.drop(columns=['displayValue'])
    bats.rename(columns={'type': 'bats', 'abbreviation': 'B'}, inplace=True)

    throws = players['throws'].values.tolist()
    throws2 = list()
    for i in throws:
        throws2.append(i) if not isinstance(i, float) else throws2.append(
            {'type': 'RIGHT', 'abbreviation': 'R', 'displayValue': 'Right'})
    throws = throws2
    throws = pd.DataFrame.from_dict(throws)
    throws = throws.drop(columns=['displayValue'])
    throws.rename(columns={'type': 'throws', 'abbreviation': 'T'}, inplace=True)

    experience = players['experience'].values.tolist()
    experience2 = list()
    for i in experience:
        experience2.append(i) if isinstance(i, dict) else experience2.append({'years': 0})
    experience = experience2
    experience = pd.DataFrame.from_dict(experience)
    #
    birthPlace = players['birthPlace'].values.tolist()
    birthPlace2 = list()
    for i in birthPlace:
        birthPlace2.append(i) if not isinstance(i, float) else birthPlace2.append(
            {'city': 'NA', 'state': 'NA', 'country': 'NA'})
    birthPlace = birthPlace2
    birthPlace = pd.DataFrame.from_dict(birthPlace)

    players = players[['id', 'fullName', 'firstName', 'lastName', 'displayName', 'dateOfBirth', 'height', 'weight']]
    players['dateOfBirth'] = players['dateOfBirth'].str.slice(start=0,stop=10)

    players = pd.concat([players, bats, throws, birthPlace, experience], axis=1)

    # print(newplay)
    #print(players)

    table_name = "ESPNAllPlayers"
    players.to_sql(table_name, bdb.conn, if_exists='replace', index=False)

    bdb.close()


if __name__ == "__main__":
    main()
