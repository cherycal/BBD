__author__ = 'chance'

import statsapi

# statsapi.DEBUG=True
# Uncomment the above line to enable debug logging,
# for the statsapi module, which will show the endpoint URL:


#https://statsapi.mlb.com/api/v1/people?personIds=475253&season=2018&hydrate=stats(type=gameLog,season=2018,gameType=R)

#m = statsapi.player_stats(475253,'hitting','gameLog')
#print(m)


r = statsapi.league_leaders('earnedRunAverage',statGroup='pitching',season=2019,limit=100,
                            playerPool='all')

print (r)

# for t in r['teams']:
#     team_id = t['id']
#     rost = statsapi.roster(team_id)
#     print(t['name'])
#     print(type(rost))
#     print(rost)

# games = statsapi.schedule(start_date='08/02/2019',end_date='08/02/2019',team=143)
#
# for game in games:
#     game_id = game['game_id']
#     print(game_id)
#     box = statsapi.boxscore(game_id)
#     print(box)








