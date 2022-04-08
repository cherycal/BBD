import json
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()
inst = push.Push()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
out_date = now.strftime("%Y%m%d")
integer_today = int(out_date)
string_today = out_date
integer_yesterday = integer_today - 1
string_yesterday = str(integer_yesterday)
year = "2021"
nextyear = str(int(year)+ 1)
fromdate = year + "0000"
todate = nextyear + "0000"

url_name = "https://fantasy.espn.com/apis/v3/games/flb/seasons/" + \
            year + "?view=proTeamSchedules_wl"

print(url_name)
f = open("games.txt", "a")

with urllib.request.urlopen(url_name) as url:
    data = json.loads(url.read().decode())
    json_formatted = json.dumps(data, indent=2)
    #print(json_formatted)
    entries = list()
    gamedict = dict()
    for team in data['settings']['proTeams']:
        if 'proGamesByScoringPeriod' in team:
            for games in team['proGamesByScoringPeriod']:
                for game in team['proGamesByScoringPeriod'][games]:
                    away = game['awayProTeamId']
                    home = game['homeProTeamId']
                    game_time = int(game['date']) / 1000
                    game_date = time.strftime("%Y%m%d", time.localtime(game_time))
                    game_time = time.strftime("%Y%m%d%H%M%S", time.localtime(game_time))
                    game_id = game['id']
                    if gamedict.get(game_id):
                        continue
                    else:
                        entries.append([game_date, game_id, home, away, game_time])
                        gamedict[game_id] = 1

    entrystr = inst.string_from_list(entries)
    f.write(entrystr)
    print( len(entries))
    delcmd = "delete from ESPNGameData where Date > " + fromdate + " and Date < " + todate
    bdb.delete(delcmd)
    bdb.insert_many("ESPNGameData", entries)
    f.close()