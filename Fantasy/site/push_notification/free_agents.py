__author__ = 'chance'

import time

from bs4 import BeautifulSoup
from selenium import webdriver

url = "http://fantasy.espn.com/baseball/league/rosters?leagueId=162788"

driver = webdriver.Chrome('C:/Users/chery/chromedriver.exe')
driver.get(url)
time.sleep(2.5)


html = driver.page_source
soup = BeautifulSoup(html,"lxml")

#time.sleep(1)

sections = soup.find_all("section")
for section in sections:
    section_row = section.find_all('span')
    names = section.find_all('span', {'class': 'teamName truncate'})
    for name in names:
        pass

    tables = section.find_all("table",{'class':'Table2__table'})

    for table in tables:
        table_rows = table.find_all('tr')
        for tr in table_rows:
            title = tr.find('span')
            a = tr.find_all('a')
            row = [i.text for i in a]
            if (len(row)):
                print("'"+name.text + "','" + row[0] + "'")



exit(0)

