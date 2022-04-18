__author__ = 'chance'

import json
import sys
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb
import push
import fantasy
import dataframe_image as dfi
import tools
import pandas as pd

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
date8 = now.strftime("%Y%m%d")
statcast_date = now.strftime("%Y-%m-%d")

formatted_date_time = now.strftime("%Y%m%d-%H%M%S")

sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")

msg = ""


def get_page():
    year = 2022
    league = 3154
    myTeamId = 7

    statids = fantasy.get_statid_dict_by_str()

    url_name = f'https://fantasy.espn.com/apis/v3/games/flb/seasons/{year}/segments/0/leagues/{league}?' \
               f'view=mBoxscore&view=mMatchupScore&view=mRoster&view=mSettings&' \
               f'view=mStatus&view=mTeam&view=modular&view=mNav'

    print("url is: " + url_name)

    column_names = ['leagueID', 'teamId', 'team', 'stat', 'result', 'score', 'updateTime']
    entries = []

    with urllib.request.urlopen(url_name) as url:
        data = json.loads(url.read().decode())
        currentMatchupId = data["status"]["currentMatchupPeriod"]
        matchups = data["schedule"]
        # homeScore = dict()
        # awayScore = dict()
        for matchup in matchups:
            matchupId = matchup["matchupPeriodId"]
            if matchupId < currentMatchupId:
                continue
            if matchupId > currentMatchupId:
                break
            awayTeam = matchup["away"]
            homeTeam = matchup["home"]
            awayTeamId = awayTeam["teamId"]
            homeTeamId = homeTeam["teamId"]
            if awayTeamId == myTeamId or homeTeamId == myTeamId:
                if awayTeam.get("cumulativeScore"):
                    awayScore = [awayTeam["cumulativeScore"]["wins"], awayTeam["cumulativeScore"]["losses"],
                                 awayTeam["cumulativeScore"]["ties"]]
                    homeScore = [homeTeam["cumulativeScore"]["wins"], homeTeam["cumulativeScore"]["losses"],
                                 homeTeam["cumulativeScore"]["ties"]]
                    # print(f'AwayTeam: {awayTeamId} Score: {awayScore} HomeTeam: {homeTeamId} Score: {homeScore}')
                    entry = [league, awayTeamId, '', '_Summary', 'WINS', awayScore[0], formatted_date_time]
                    entries.append(entry)
                    entry = [league, homeTeamId, '', '_Summary', 'WINS', homeScore[0], formatted_date_time]
                    entries.append(entry)
                    entry = [league, homeTeamId, '', '_Summary', 'TIES', homeScore[2], formatted_date_time]
                    entries.append(entry)
                    awayStats = awayTeam["cumulativeScore"]["scoreByStat"]
                    homeStats = homeTeam["cumulativeScore"]["scoreByStat"]
                    for stat in awayStats:
                        if awayStats[stat].get('result'):
                            # print(
                            #      f'TeamId: {awayTeamId} StatId: {statids[stat]} Result: {awayStats[stat]["result"]} Score: {awayStats[stat]["score"]}')
                            # print(
                            #     f'TeamId: {homeTeamId} StatId: {statids[stat]} Result: {homeStats[stat]["result"]} Score: {homeStats[stat]["score"]}')
                            entry = [league, awayTeamId, '', statids[stat], awayStats[stat]["result"],
                                     awayStats[stat]["score"], formatted_date_time]
                            entries.append(entry)
                            entry = [league, homeTeamId, '', statids[stat], homeStats[stat]["result"],
                                     homeStats[stat]["score"], formatted_date_time]
                            entries.append(entry)

        df = pd.DataFrame(entries, columns=column_names)

        table_name = "FLIPCurrentScores"
        df.to_sql(table_name, bdb.conn, if_exists='replace', index=False)

        lol = []
        index = list()
        col_headers, rows = bdb.select_w_cols("select TeamName, Result, Score from FLIPScoreView where stat = '_Summary'")

        for row in rows:
            lol.append(row)
            index.append("")

        df = pd.DataFrame(lol, columns=col_headers, index=index)

        img = "mytable.png"
        dfi.export(df, img)
        inst.tweet_media(img, "FLIP score summary: " + str(formatted_date_time))


def main():
    get_page()
    driver.close()
    bdb.close()


if __name__ == "__main__":
    main()
