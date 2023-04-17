__author__ = 'chance'
import sys
sys.path.append('./modules')
import sqldb

# My python class: sqldb.py
mode = "PROD"
if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')
# name = "Javier Assad"


data = bdb.select_table("ACheck_ID")

existing_id_query = bdb.select('select IDPLAYER from IDMap where MLBID in ( select mlbid from ACheck_ID )')
existing_ids = list()
for row in existing_id_query:
    existing_ids.append(row[0])

column_names = ["mlbid", "fullName", "firstName","lastName","birthDate", "currentAge", "birthCountry", "active", "primaryPosition", "bats",
                "throws", "draftYear"]

# IDPLAYER,PLAYERNAME,BIRTHDATE,FIRSTNAME,LASTNAME,TEAM,LG,POS,IDFANGRAPHS,FANGRAPHSNAME,MLBID,MLBNAME,ESPNID,ESPNNAME,BATS,THROWS,ACTIVE

print(data['column_names'])

player_data = dict()

for d in data['dicts']:
    mlbid = str( d['mlbid'])
    player_data[mlbid] = dict()
    player_data[mlbid]["IDPLAYER"] = mlbid
    player_data[mlbid]["MLBID"] = mlbid
    player_data[mlbid]["PLAYERNAME"] = d['name']
    player_data[mlbid]["MLBNAME"] = d['name']
    player_data[mlbid]["TEAM"] = d['mlbTeam']
    player_data[mlbid]["POS"] = d['position']
    player_data[mlbid]["BATS"] = d['bats']
    player_data[mlbid]["THROWS"] = d['throws']
    if d['type'] == "FG":
        player_data[mlbid]["type"] = "FG"
        player_data[mlbid]["IDFANGRAPHS"] = d['alt_id']
        player_data[mlbid]["FANGRAPHSNAME"] = d['name']
    if d['type'] == "ESPN":
        player_data[mlbid]["type"] = "ESPN"
        player_data[mlbid]["ESPNID"] = d['alt_id']
        player_data[mlbid]["ESPNNAME"] = d['name']
    player_data[mlbid]["ACTIVE"] = "Y"

for pid in player_data:
    if pid in existing_ids:
        cmd = ""
        params = list()
        print(pid, player_data[pid].get("type"))
        if player_data[pid].get("type") == "FG":
            cmd = "UPDATE IDMap set TEAM = ? , POS = ?, BATS = ?, THROWS = ?, IDFANGRAPHS = ?, FANGRAPHSNAME = ? where IDPLAYER = ?"
            params = ( player_data[pid].get("TEAM",None),
                  player_data[pid].get("POS", None),
                  player_data[pid].get("BATS", None),
                  player_data[pid].get("THROWS", None),
                  player_data[pid].get("IDFANGRAPHS", None),
                  player_data[pid].get("FANGRAPHSNAME", None),
                  player_data[pid].get("IDPLAYER"))
        elif player_data[pid].get("type") == "ESPN":
            cmd = "UPDATE IDMap set TEAM = ? , POS = ?, BATS = ?, THROWS = ?, ESPNID = ?, ESPNNAME = ? where IDPLAYER = ?"
            params = (player_data[pid].get("TEAM", None),
                      player_data[pid].get("POS", None),
                      player_data[pid].get("BATS", None),
                      player_data[pid].get("THROWS", None),
                      player_data[pid].get("ESPNID", None),
                      player_data[pid].get("ESPNNAME", None),
                      player_data[pid].get("IDPLAYER"))

        print(cmd,params)
        bdb.execute(cmd, params)
    else:
        cmd = "INSERT INTO IDMap (IDPLAYER,PLAYERNAME,TEAM,POS,IDFANGRAPHS,FANGRAPHSNAME,MLBID,MLBNAME,ESPNID,ESPNNAME,BATS,THROWS,ACTIVE) values " \
              "(?,?,?,?,?,?,?,?,?,?,?,?,?)"
        params = (player_data[pid].get("IDPLAYER"),player_data[pid].get("PLAYERNAME"),player_data[pid].get("TEAM", None),
                  player_data[pid].get("POS", None),player_data[pid].get("IDFANGRAPHS", None),player_data[pid].get("FANGRAPHSNAME", None),
                  player_data[pid].get("IDPLAYER"), player_data[pid].get("PLAYERNAME"),
                  player_data[pid].get("ESPNID", None), player_data[pid].get("ESPNNAME", None), player_data[pid].get("BATS", None),
                  player_data[pid].get("THROWS", None),"Y")
        bdb.execute(cmd, params)

bdb.close()
