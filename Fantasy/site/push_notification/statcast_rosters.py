__author__ = 'chance'

import json
import urllib.request

geourl = "http://statsapi.mlb.com/api/v1/teams"
#response = urllib.request.urlopen(geourl)

response = urllib.request.urlopen(geourl)

content = response.read()
data = json.loads(content.decode("utf8"))
teams = data['teams']

teamlinks = []
playerlinks = []

for team in teams:
    league = team['league']
    if (league.get('name')):
        league_name = league['name']
    if( league_name == 'American League' or league_name == 'National League'):
        #print(team['id'])
        #print(team['name'])
        #print(team['link'])
        #print(league_name)
        roster_link = str("http://statsapi.mlb.com" + team['link'] + \
                                                     '/roster/fullRoster?season=2019')
        teamlinks.append(roster_link)
        #print(roster_link)
        #print("")

for teamlink in teamlinks:
    #print(teamlink)
    response = urllib.request.urlopen(teamlink)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    roster = data['roster']

    for person in roster:
        print(person)