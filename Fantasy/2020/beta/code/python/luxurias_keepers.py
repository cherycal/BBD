import urllib.request, json
import time
from datetime import datetime

#print("Load start ")
now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%m%d%Y-%H%M%S")
#print(now)
#print(date_time)

with urllib.request.urlopen("http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/162788?view=roster") as url:
    data = json.loads(url.read().decode())

#print(type(data))

#print(data.keys())

#print(  data['teams'][0]['roster']['entries'][0]['playerPoolEntry']['player']['fullName'])

#for team in data['teams']:
#team = data['teams'][5]
#print( "Team: " + team['nickname'])

for team in data['teams']:
    if team['id'] == 4:
        team_name = team['location'] + " " + team['nickname'] + " (" + str(team['id']) + ")"
        print(team_name)
        for player in team['roster']['entries']:
            player_full_name = player['playerPoolEntry']['player']['fullName'] 
            #print( player['playerPoolEntry']['player']['fullName'] )
            #print( player['playerPoolEntry'].keys() )
            keeper_value = player['playerPoolEntry']['keeperValue']
            for pool_entry_key in player['playerPoolEntry'].keys():
                #print( pool_entry_key )
                if pool_entry_key != "player":
                    pass
                    #print( player['playerPoolEntry'][pool_entry_key])
                else:
                    #print( player['playerPoolEntry'][pool_entry_key].keys())
                    for player_key in player['playerPoolEntry']['player'].keys():
                        #print(player_key)
                        if player_key != "ownershipHistory":
                            pass
                            #print(player['playerPoolEntry']['player'][player_key])
                        else:
                            for item in player['playerPoolEntry']['player'][player_key]:
                                item_date = time.localtime(item['date'] / 1000)
                                history_date = time.strftime('%Y%m%d', item_date)
                                percent_owned = round(item['percentOwned'],2)
                                auction_value = round(item['auctionValueAverage'],2)
                                print(team_name + " , " + player_full_name + " , " + history_date + " , " +
                                      str(percent_owned) + " , " + str(auction_value) + " , " + str(keeper_value))
                        
                
    #print("\n\n")
    
#print("Done loading")
now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%m%d%Y-%H%M%S")
#print(time.time())
#print(date_time)
