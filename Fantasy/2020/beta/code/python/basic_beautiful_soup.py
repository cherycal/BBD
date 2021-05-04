__author__ = 'chance'

import sys
sys.path.append('./modules')
import requests
from bs4 import BeautifulSoup as bs
import tools
import time
import push
inst = push.Push()

sleep_interval = 5


#url = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=&splitArrPitch=&position=B&autoPt=true&splitTeams=false&statType=player&statgroup=1&startDate=2020-03-01&endDate=2020-11-01&players=&filter=&groupBy=season&sort=-1,1"
url = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=1&splitArrPitch=&position=B&autoPt=true&splitTeams=false&statType=player&statgroup=1&startDate=2020-03-01&endDate=2020-11-01&players=&filter=&groupBy=season&sort=-1,1"
# Selenium
driver = tools.get_driver("headless")
driver.get(url)
time.sleep(sleep_interval)
html = driver.page_source

soup = bs(html, "html.parser")
results = soup.find_all('a', attrs={"class":"data-export"})
print(results[0]['href'])

driver.close()