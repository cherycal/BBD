__author__ = 'chance'
import sys
sys.path.append('./modules')
import json
from io import BytesIO

import certifi
import pycurl

import fantasy
mode = "PROD"
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()

gamedate = dict()
date8 = fantasy.get_date8()

c = bdb.select("select GameID, Date from ESPNGameData")
for row in c:
    [gm,dt] = row
    gamedate[str(gm)] = str(dt)


leagueID = "6455"

# url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/" + "2021" + \
#            "/segments/0/leagues/" + \
#            str(leagueID) + "?view=kona_playercard"

url_name = "https://fantasy.espn.com/apis/v3/games/flb/" \
           "seasons/2021/segments/0/leagues/37863846?" \
           "scoringPeriodId=20&view=kona_player_info"

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

player_data_json = json.loads(data)


for player in player_data_json['players']:
    if player.get('player'):
        if player['player'].get('starterStatusByProGame'):
            for game in player['player']['starterStatusByProGame']:
                if player['player']['starterStatusByProGame'][game] == 'PROBABLE':
                    if gamedate.get(game):
                        if gamedate[game] > date8:
                            print(player['player']['fullName'])
                            print(player['player']['id'])
                            print(game)
                            print(gamedate[game])
                            print("\n")
                            break

print("Done")
