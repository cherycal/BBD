__author__ = 'chance'

import time
import csv
import sys

import urllib.request
from datetime import datetime

sys.path.append('./modules')
from bs4 import BeautifulSoup
from selenium import webdriver
import push

sz = 25
cols = 15
my_results = [None] * sz
for i in range(0,sz-1):
    my_results[i] = [None] * cols

out_file = 'totals2.csv'
w_a = 'a'

inst = push.Push()
sleep_interval = 7

driver = webdriver.Chrome('C:/Users/chery/chromedriver.exe')

scoring_intervals = [138]
print = 1

for scoring_interval in scoring_intervals:

    url = "http://fantasy.espn.com/baseball/team?leagueId=162788&seasonId=2019&teamId=4&fromTeamId=4" \
          "&scoringPeriodId=" + str(scoring_interval)

    driver.get(url)
    time.sleep(sleep_interval)

    html = driver.page_source
    soup = BeautifulSoup(html,"lxml")

    team_span = soup.find_all("span", {"class": "teamName truncate"})
    team_name = team_span[0].text

    my_th = soup.find_all("th",{"class": "tc bg-clr-white Table2__th"})
    my_dt = my_th[1].text

    my_data = soup.find_all("tr",{"class":"Table2__tr Table2__tr--lg Table2__odd"})
    my_data_dict = {}

    iter = 0
    count = 0
    batlines = 14
    pitchlines = 10
    lines = batlines
    j = 0
    batting = {}
    pitching = {}
    for i in my_data:
        if (int( i['data-idx'] ) < lines ):
            if( int(i['data-idx']) == 0 ):
                j = 0
                iter += 1
            my_ds = []
            my_divs = i.find_all("div")
            for ds in my_divs:
                my_ds.append(ds.text)
            if( ( iter == 1 or iter == 4 ) and len(my_ds) > 6):
                my_ds = [my_dt, str(scoring_interval), '', my_ds[0],my_ds[6]]
            if(iter == 1):
                batting[str(j)] = my_ds
            if(iter == 2 or iter == 3 ):
                dc = 0
                for d in my_ds:
                    batting[str(j)].append(d)
                    if(iter == 2 and dc == 8):
                        batting[str(j)].append('')
                    dc += 1
                batting[str(j)][0] = my_dt
                batting[str(j)][1] = team_name
                batting[str(j)][2] = "B"
            if( iter == 4):
                lines = pitchlines
                pitching[str(j)] = my_ds
            if(iter > 4 ):
                for d in my_ds:
                    pitching[str(j)].append(d)
                pitching[str(j)][0] = my_dt
                pitching[str(j)][1] = team_name
                pitching[str(j)][2] = "P"
            count += 1
            j += 1

    batcell = str(batlines-1)
    pitchcell = str( pitchlines -1)
    battotal = batting[batcell][len(batting[batcell]) - 1]
    if (battotal == "--"):
        battotal = "0"
    pitchtotal = pitching[pitchcell][len(pitching[pitchcell])-1]
    if(pitchtotal == "--"):
        pitchtotal = "0"


    print(pitching[pitchcell])
    totline = str(int(pitchcell)+1)
    print(totline)
    pitching[totline] = pitching[pitchcell].copy()

    pitching[totline][len(pitching[pitchcell])-1] = str( int( pitchtotal ) + int( battotal ) )
    pitching[totline][2] = "T"
    pitching[totline][3] = "TOT"

    pitching[pitchcell][2] = "P_TOT"
    pitching[pitchcell][3] = "PITCH_TOTAL"
    batting[batcell][2] = "B_TOT"
    batting[batcell][3] = "BAT_TOTAL"

    if(print):

        with open(out_file, w_a, newline='') as output:
            csv_writer = csv.writer(output)

            for i in range(0,batlines):
                print(batting[str(i)])
                csv_writer.writerow(batting[str(i)])

            for i in range(0,pitchlines+1):
                print(pitching[str(i)])
                csv_writer.writerow(pitching[str(i)])



driver.close()
exit(0)




