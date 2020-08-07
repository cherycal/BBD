__author__ = 'chance'

import time
import csv
import tools
from selenium import webdriver

from bs4 import BeautifulSoup
import push

sz = 30
cols = 15
my_results = [None] * sz
for i in range(0,sz-1):
    my_results[i] = [None] * cols

out_file = 'totals.csv'
w_a = 'w'

#inst = push.Push()
sleep_interval = 7

#driver = webdriver.Chrome('C:/Users/chery/chromedriver.exe')
driver = tools.get_driver()

# 3-8, 111-114 are off days

scoring_intervals = [163]
printflag = 1

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
    battotalrow = 0
    pitchtotalrow = 0

    j = 0
    batting = {}
    pitching = {}
    total = {}
    datapoints = 0
    maxlines = 25
    totcolumn = 17

    for i in my_data:
        if (int( i['data-idx'] ) > datapoints):
            datapoints = int( i['data-idx'] )
        if (int( i['data-idx'] ) < maxlines ):
            if( int(i['data-idx']) == 0 ):
                j = 0
                iter += 1
            row = str(j)
            my_ds = []
            my_divs = i.find_all("div")
            for ds in my_divs:
                div_text = ds.text
                if (div_text == "" or div_text == "--"):
                    div_text = "0"
                my_ds.append(div_text)
            #print(my_ds)
            if( ( iter == 1 or iter == 4 ) and len(my_ds) > 6):
                my_ds = [my_dt, str(scoring_interval), '', my_ds[0],my_ds[6]]
            if( ( iter == 1 or iter == 4 ) and my_ds[3] == 'TOTALS'):
                my_ds = [my_dt, str(scoring_interval), '', my_ds[0], my_ds[3]]
            if(iter == 1):
                batting[row] = my_ds
            if(iter == 2 or iter == 3 ):
                dc = 0
                for d in my_ds:
                    batting[row].append(d)
                    if(iter == 2 and dc == 8):
                        batting[row].append('0')
                    dc += 1
                batting[row][0] = my_dt
                batting[row][1] = team_name
                if (batting[row][4] != "TOTALS"):
                    batting[row][2] = "B"
                else:
                    batting[row][2] = "BT"
                    batting[row][3] = "BATTING_TOTAL"
                    totcolumn = len(batting[row]) - 1
                    battotal = batting[row][totcolumn]
                    if (battotal == "" or battotal == "--"):
                        battotal = "0"
            if( iter == 4):
                datapoints = 0
                lines = datapoints
                #print(my_ds)
                pitching[row] = my_ds
            if(iter > 4 ):
                for d in my_ds:
                    pitching[row].append(d)
                pitching[row][0] = my_dt
                pitching[row][1] = team_name
                if (pitching[row][4] != "TOTALS"):
                    pitching[row][2] = "P"
                else:
                    pitching[row][2] = "PT"
                    pitching[row][3] = "PITCHING_TOTAL"
                    totcolumn = len(pitching[row]) - 1
                    pitchtotal = pitching[row][totcolumn]
                    if (pitchtotal == "" or pitchtotal == "--" ):
                        pitchtotal = "0"
                    total["0"] = pitching[row].copy()
                    total["0"][2] = "T"
                    total["0"][3] = "TOTAL"
            count += 1
            j += 1

    total["0"][totcolumn] = str( int( pitchtotal ) + int( battotal ) )

    if(printflag):

        with open(out_file, w_a, newline='') as output:
            csv_writer = csv.writer(output)

            for i in range(0,len(batting)):
                out_list = batting[str(i)]
                out_list.insert(0,str(scoring_interval))
                print(out_list)
                csv_writer.writerow(out_list)

            for i in range(0,len(pitching)):
                out_list = pitching[str(i)]
                out_list.insert(0, str(scoring_interval))
                print(out_list)
                csv_writer.writerow(out_list)


            out_list = total["0"]
            out_list.insert(0, str(scoring_interval))
            print(out_list)
            csv_writer.writerow(out_list)

driver.quit()
exit(0)

