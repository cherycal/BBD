__author__ = 'chance'

import requests
from bs4 import BeautifulSoup

page = requests.get('http://fantasy.espn.com/baseball/league/rosters?leagueId=87301')

soup = BeautifulSoup(page.text, 'html.parser')

print(soup.find_all())