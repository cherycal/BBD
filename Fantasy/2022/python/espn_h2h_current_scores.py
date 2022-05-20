__author__ = 'chance'

import sys
from datetime import datetime

sys.path.append('./modules')

from bs4 import BeautifulSoup as bs
import tools
import sqldb
import push
import time
import random
import pandas as pd

inst = push.Push()
bdb = sqldb.DB('Baseball.db')

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
date8 = now.strftime("%Y%m%d")
statcast_date = now.strftime("%Y-%m-%d")

# Selenium
driver = tools.get_driver("headless")


def get_points_page(sleep_interval, matchupPeriodId, season, teamId, leagueId):
    formatted_date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    url = f'https://fantasy.espn.com/baseball/boxscore?leagueId={leagueId}&matchupPeriodId={matchupPeriodId}&seasonId={season}&teamId={teamId}'
    print(f'{url} at {formatted_date_time}')

    try:
        driver.get(url)
        time.sleep(sleep_interval)
        html = driver.page_source
        soup = bs(html, "html.parser")
        teams = soup.find_all('span', {"class":
                                           ["team-name truncate"]})

        scores = soup.find_all('div', {"class": ["team-score flex justify-between items-start flex-column",
                                                 "team-score flex justify-between items-end flex-column"]})

        diff = int(scores[0].text) - int(scores[1].text)
        msg = f'{teams[0].text[0:10]} {scores[0].text}, {teams[1].text[0:10]} {scores[1].text} ({diff})\n'

        inst.push("PTS score", msg)
        inst.tweet(msg)
    except Exception as ex:
        print(str(ex))
        inst.push(f'Error in h2h_scores {str(ex)}')
        # inst.tweet(f'Error in h2h_scores {str(ex)}')


def get_cats_page(sleep_interval, matchupPeriodId, season, teamId, leagueId):
    formatted_date_time = datetime.now().strftime("%Y%m%d-%H%M%S")

    url = f'https://fantasy.espn.com/baseball/boxscore?leagueId={leagueId}&matchupPeriodId={matchupPeriodId}&seasonId={season}&teamId={teamId}'
    print(f'{url} at {formatted_date_time}')

    try:
        driver.get(url)
        time.sleep(sleep_interval)
        html = driver.page_source
        soup = bs(html, "html.parser")
        results = soup.find_all('div', {"class":
                                            ["jsx-2810852873 table--cell pl2 away-team-name team-name truncate",
                                             "jsx-2810852873 table--cell pl2 fw-bold team-score",
                                             "jsx-2810852873 table--cell pl2 home-team-name team-name truncate",
                                             "jsx-2810852873 table--cell pl2 fw-bold team-score cell-highlight"]})

        if len(results) > 3:
            msg = f'{results[0].text[0:10]} {results[1].text}, {results[2].text[0:10]} {results[3].text}\n'

            inst.push("H2H score", msg)
            inst.tweet(msg)

        results = soup.find_all('table', {'class': ["Table"]})

        lol = list()
        if len(results) > 0:
            for child in results[0].children:
                for td in child:
                    if td:
                        st_list = list()
                        for i in td:
                            st_list.append(i.text)
                        if len(st_list):
                            lol.append(st_list)

            col_headers = lol.pop(0)
            # print(lol)
            col_headers[15] = "HRVS"

            df = pd.DataFrame(lol, columns=col_headers)
            df['updateTime'] = formatted_date_time

            table_name = "FLIPCurrentScores"
            bdb.delete(f'delete FROM {table_name}')
            df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
    except Exception as ex:
        print(str(ex))
        inst.push(f'Error in h2h_scores {str(ex)}')
    # inst.tweet(f'Error in h2h_scores {str(ex)}')


def main():
    loop_sleep = 240
    MIN_SLEEP = 15
    MAX_SLEEP = 25
    matchupPeriodId = 6
    season = 2022
    cats_teamId = 7
    cats_leagueId = 3154
    points_teamId = 8
    points_leagueId = 1305684057
    points_teamId2 = 35
    points_leagueId2 = 2692
    while True:
        ts = datetime.now()
        time6 = ts.strftime("%H%M%S")
        current_time = int(time6)
        sleep_interval = random.randint(MIN_SLEEP, MAX_SLEEP)
        get_cats_page(sleep_interval, matchupPeriodId, season, cats_teamId, cats_leagueId)
        get_points_page(sleep_interval, matchupPeriodId, season, points_teamId, points_leagueId)
        get_points_page(sleep_interval, matchupPeriodId, season, points_teamId2, points_leagueId2)
        time.sleep(loop_sleep)
        if current_time >= 211500:
            driver.close()
            break

    exit(0)


if __name__ == "__main__":
    main()
