__author__ = 'chance'

import json
import sys
import urllib.request

import pandas as pd

sys.path.append('./modules')
import sqldb
import push
import fantasy
from datetime import date, datetime
from datetime import timedelta

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

sleep_interval = 1
# Selenium
# driver = tools.get_driver("headless")

msg = ""


def get_odds_page(date_, datetime_):
    url_name = f"https://site.web.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?" \
               f"region=us&lang=en&contentorigin=espn&limit=100&calendartype=offdays" \
               f"&dates={date_}&tz=America%2FNew_York"
    print("url is: " + url_name)
    with urllib.request.urlopen(url_name) as url:
        data = json.loads(url.read().decode())
        if data.get('events'):
            gameslist = list()
            lol = []
            for event in data['events']:
                temperature = None
                indoor = None
                espn_gameid = event.get('id', None)
                homeTeam = None
                awayTeam = None
                homeStarter = None
                homeStarterId = None
                awayStarter = None
                awayStarterId = None
                overUnder = None
                awayOdds = None
                homeOdds = None
                details = None
                fav = None
                ml = None
                if event.get('weather'):
                    temperature = event['weather'].get('temperature')
                if event.get('competitions'):
                    for game in event['competitions']:
                        if game.get('competitors'):
                            # print(game['competitors'])
                            for team in game['competitors']:
                                if team['homeAway'] == 'home':
                                    homeTeam = team['team']['abbreviation']
                                    if team.get('probables'):
                                        homeStarter = team['probables'][0]['athlete']['fullName']
                                        homeStarterId = team['probables'][0]['athlete']['id']
                                else:
                                    awayTeam = team['team']['abbreviation']
                                    if team.get('probables'):
                                        awayStarter = team['probables'][0]['athlete']['fullName']
                                        awayStarterId = team['probables'][0]['athlete']['id']
                        if game.get('venue'):
                            indoorbool = game["venue"]['indoor']
                            if homeTeam == 'BAL':
                                indoorbool = False
                        providerName = ""
                        if game.get('odds'):
                            priority = -1
                            for provider in game['odds']:
                                if provider.get('provider'):
                                    if provider['provider'].get('priority') and provider['provider']['priority'] > priority:
                                        if provider.get('details'):
                                            details = provider['details']
                                            if details == "EVEN":
                                                fav = homeTeam
                                                ml = '-100'
                                            else:
                                                [fav, ml] = details.split(' ')
                                        priority = provider['provider']['priority']
                                        providerName = provider['provider']['name']
                                        overUnder = provider.get('overUnder', None)
                                        if provider.get('homeTeamOdds'):
                                            homeOdds = provider.get('homeTeamOdds').get('moneyLine', None)
                                        if provider.get('awayTeamOdds'):
                                            awayOdds = provider.get('awayTeamOdds').get('moneyLine', None)
                                indoor = "Indoor" if indoorbool else "Outdoor"
                        if fav:
                            if fav == homeTeam:
                                homeOdds = ml
                                awayOdds = ml.replace('-','+')
                            else:
                                awayOdds = ml
                                homeOdds = ml.replace('-','+')
                        homeOddslist = [datetime_, date_, espn_gameid, providerName, temperature, indoor, 'Home',
                                        homeTeam,homeStarter, homeStarterId, homeOdds, overUnder, details]
                        awayOddslist = [datetime_, date_, espn_gameid, providerName, temperature, indoor, 'Away',
                                        awayTeam, awayStarter, awayStarterId, awayOdds, overUnder, details]
                        if ml and overUnder:
                            gameslist.append(espn_gameid)
                            lol.append(homeOddslist)
                            lol.append(awayOddslist)
                            print(f"{homeOddslist}")
                            print(f"{awayOddslist}")
        oddscols = ["update_time", "gamedate", "espn_gameid", "providerName", "temperature", "indoor", "Team",
                    "HomeAway", "Starter", "StarterId", "ML", "overUnder", "details"]
        gamestuple = tuple(gameslist)

        df = pd.DataFrame(lol, columns=oddscols)
        table_name = "ESPNOdds"
        command = f"Delete from ESPNOdds where espn_gameid in {str(gamestuple)}"
        if len(gamestuple):
            df.to_sql(table_name, bdb.conn, if_exists='append', index=False)


def get_dates():
    # Optional way to create list of dates
    # print("Range of dates")
    # start_date = date.today()
    # end_date = start_date + timedelta(days=3)
    # datelist = [(date.fromordinal(i).strftime('%Y%m%d')) for i in range(start_date.toordinal(), end_date.toordinal())]

    datelist = list()
    DAYS_AHEAD = 3
    count = 0
    dt = date.today()
    datelist.append(dt.strftime('%Y%m%d'))
    while count < DAYS_AHEAD:
        dt = dt + timedelta(days=1)
        count += 1
        datelist.append(dt.strftime('%Y%m%d'))
    return datelist


def get_db_odds(date8):
    data = bdb.select_plus(f"select espn_gameid, details from ESPNOdds where gamedate = {date8}")
    print(data)
    exit(0)


def main():
    now = datetime.now()  # current date and time
    date_time = now.strftime("%Y%m%d%H%M%S")
    dates = get_dates()
    OVERRIDE = False
    if OVERRIDE:
        dates = ["20230425"]

    for date8 in dates:
        get_odds_page(date8, date_time)


# driver.close()


if __name__ == "__main__":
    main()
