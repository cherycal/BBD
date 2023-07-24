__author__ = 'chance'

import time

from bs4 import BeautifulSoup

import push
import tools

inst = push.Push()

sleep_interval = 20


url = "https://fantasy.espn.com/baseball/league/rosters?leagueId=37863846"

driver = tools.get_driver()
driver.get(url)
time.sleep(sleep_interval)
html = driver.page_source
soup = BeautifulSoup(html, "lxml")

sections = soup.find_all("section")
for section in sections:
    section_row = section.find_all('span')
    names = section.find_all('span', {'class': 'teamName truncate'})
    for name in names:
        pass

    tables = section.find_all("table", {'class': 'Table2__table'})

    for table in tables:
        table_rows = table.find_all('tr')
        for tr in table_rows:
            title = tr.find('span')
            a = tr.find_all('a')
            row = [i.text for i in a]
            if (len(row)):
                command = "INSERT INTO Rosters(Player, Team, LeagueID) VALUES ( \"" + row[0] + \
                          "\" ,\"" \
                                                                                   + \
                          name.text + "\"," + str('league_name') + ")"
                #new_rosters[row[0]+':'+name.text] = name.text
                print(command)
                #insert_list.append(command)

driver.close()