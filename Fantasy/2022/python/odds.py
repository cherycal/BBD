import re
import sys
from datetime import datetime

import pandas as pd

sys.path.append('./modules')
import sqldb
import push
import fantasy
from operator import itemgetter
import unidecode
import pytz
from datetime import date
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()


def process_oddsline(text):
    #print(f'text: {text}')
    splittext = re.split('(SF)|(Giants)|'
                         '(SD)|(Padres)|'
                         '(HOU)|(Astros)|'
                         '(BAL)|(Orioles)|'
                         '(KC)|(Royals)|'
                         '(NY)|(Yankees)|'
                         '(Mets)|'
                         '(BOS)|(Red Sox)|'
                         '(TB)|(Rays)|'
                         '(TOR)|(Blue Jays)|'
                         '(ATL)|(Braves)|'
                         '(OAK)|(Athletics)|'
                         '(TEX)|(Rangers)|'
                         '(LA)|(Angels)|'
                         '(Dodgers)|'
                         '(OAK)|(Athletics)|'
                         '(SEA)|(Mariners)|'
                         '(COL)|(Rockies)|'
                         '(MIL)|(Brewers)|'
                         '(ARI)|(Diamondbacks)|'
                         '(MIN)|(Twins)|'
                         '(CHI)|(White Sox)|(Cubs)|'
                         '(PHI)|(Phillies)|'
                         '(PIT)|(Pirates)|'
                         '(WAS)|(Nationals)|'
                         '(BOS)|(Red Sox)|'
                         '(STL)|(Cardinals)|'
                         '(MIA)|(Marlins)|'
                         '(CLE)|(Guardians)|'
                         '(CIN)|(Reds)|(\d+:\d\dAM)|(\d+:\d\dPM)|'
                         '(DET)|(Tigers)|'
                         'O (\d\d\.\d)([\+]\d\d\d)|'
                         'U (\d\d\.\d)([\+]\d\d\d)|'
                         'O (\d\d\.\d)([\−]\d\d\d)|'
                         'U (\d\d\.\d)([\−]\d\d\d)|'
                         'O (\d\d\.\d)([−]\d\d\d)|'
                         'U (\d\d\.\d)([−]\d\d\d)|'
                         'O (\d\.\d)([\+]\d\d\d)|'
                         'U (\d\.\d)([\+]\d\d\d)|'
                         'O (\d)([\+]\d\d\d)|'
                         'U (\d)([\+]\d\d\d)|'
                         'O (\d\d)([\+]\d\d\d)|'
                         'U (\d\d)([\+]\d\d\d)|'
                         'O (\d\.\d)([\-]\d\d\d)|'
                         'U (\d\.\d)([\-]\d\d\d)|'
                         #'(\-\d\d\d)|'
                         'O (\d\d)([\-]\d\d\d)|'
                         'U (\d\d)([\-]\d\d\d)|'
                         '(\d\.\d)|(\−\d\d\d)|'
                         '(\d\d\.\d)|(\−\d\d\d)|'
                         #'(\d)(\-\d\d\d)|'
                         '-\d+\.?\d+-\d+|\+\d+\.?\d+-\d+|'
                         ' +|\xa0|'
                         '(-\d+\.?\d+)|'
                         '\+', text)

    res = [i for i in splittext if i]

    if len(res) == 10:
        r1 = res[8][0]
        r2 = res[8][1:]
        res.append(res[9])
        res[8] = r1
        res[9] = r2
        res[10].replace('−','-')
        if res[10][0] == '−':
            res[10] = '-' + res[10][1:]

        # if res[9][0] == '−':
        #     res[9] = int(res[9][1:]) * -1
        # else:
        #     res[9] = int(res[9])
        # if res[10][0] == '−':
        #     res[10] = int(res[10][1:]) * -1
        # else:
        #     res[10] = int(res[10])

    print(f'res:{res}:')

    return res


def run_odds():
    utc_now = datetime.now(pytz.UTC)
    dt = date.today()
    #dt8 = dt.strftime("%Y%m%d")

    dt8 = utc_now.strftime("%Y%m%d")
    odds_update_time = utc_now.strftime("%Y%m%d%H%M%S")

    # https://sportsbook.draftkings.com//sites/US-SB/api/v5/eventgroups/84240?format=json
    url = "https://sportsbook.draftkings.com/leagues/baseball/2003?category=game-lines-&subcategory=game"
    #url = "https://sportsbook.draftkings.com/leagues/baseball/mlb"
    dfs = pd.read_html(url)
    tbl = dfs[0]

    entries = []
    column_names = ["date", "name", "time", "Tm", "Team", "OU", "ML", "UpdateTime"]
    table_name = "Odds"

    count = 0
    for i in dfs:
        #print(f'dt: {dt8}, i: {i}')
        oddslines = i.iloc[:, 0:4]
        for oddsline in oddslines.values:
            #print(f'oddsline: {oddsline}')
            oddslist = process_oddsline(' '.join(map(str, oddsline)))

            if len(oddslist) > 10:
                #print(f'oddslist2: {oddslist}')
                if any(char.isdigit() for char in oddslist[5]):
                    name = f'{oddslist[3]} {oddslist[4]}'
                else:
                    name = f'{oddslist[3]} {oddslist[4]} {oddslist[5]}'
                name = unidecode.unidecode(name)
                odds = list(itemgetter(0, 1, 2, -3, -1)(oddslist))
                odds.insert(0, name)
                odds.insert(0, dt8)
                odds.append(odds_update_time)
                if odds[4] == "Yankees":
                    odds[3] = "NYY"
                if odds[4] == "Mets":
                    odds[3] = "NYM"
                if odds[4] == "Angels":
                    odds[3] = "LAA"
                if odds[4] == "Dodgers":
                    odds[3] = "LAD"
                if odds[4] == "Cubs":
                    odds[3] = "CHC"
                if odds[4] == "White Sox":
                    odds[3] = "CHW"
                if odds[2][-1] == "M":
                    if len(odds) > 6 and odds[6][0] == '−':
                        #print(ord(odds[6][0]))
                        odds[6] = '-'+odds[6][1:]
                        #print(ord(odds[6][0]))
                    bdb.insert_list(table_name, odds, verbose=False)
                    entries.append(odds)
        #if count == 0:
        #dt = dt + timedelta(days=1)
        #dt8 = dt.strftime("%Y%m%d")
        #count += 1

    df = pd.DataFrame(entries, columns=column_names)
    #df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
    print(df)

    tables = ['UpcomingStartsWithStats']

    for tbl in tables:
        try:
            bdb.table_to_csv(tbl)
        except Exception as ex:
            print(f'Error in table_to_csv {tbl}: {ex}')

    bdb.close()


def main():
    run_odds()


if __name__ == "__main__":
    main()
