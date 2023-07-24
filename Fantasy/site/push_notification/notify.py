__author__ = 'chance'

import time

from bs4 import BeautifulSoup

import push
import tools

inst = push.Push()

o_pts = new_o_pts = 0
sleep_interval = 2

url = "http://fantasy.espn.com/baseball/team?leagueId=162788&seasonId=2019&teamId=4&fromTeamId=4"

driver = tools.get_driver()
driver.get(url)
time.sleep(7)

while(1):
    print("Check: " + str(o_pts))
    html = driver.page_source
    soup = BeautifulSoup(html,"lxml")
    my_data = soup.find_all("span", {"class": "team-record ttl"})
    if len( my_data) > 0:
        new_o_pts = my_data[0].get_text()[:-4]
        if( new_o_pts != o_pts ):
            chg = int(new_o_pts) - int(o_pts)
            print("Chg: " + str(chg))
            print("New: " + str(new_o_pts))
            inst.push_change(chg, "TOT PTS", str(new_o_pts))
            o_pts = new_o_pts
    else:
        print("Failed get")
    driver.refresh()
    time.sleep(60)

