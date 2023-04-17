__author__ = 'chance'

import sys

sys.path.append('../modules')
import requests
from bs4 import BeautifulSoup

sleep_interval = 1


msg = ""

def get_page():
	url = "https://fantasy.espn.com/baseball/watchlist?leagueId=2692"
	print("url is: " + url)



	r = requests.get(url)

	soup = BeautifulSoup(r.content,
	                     'html5lib')  # If this line causes an error, run 'pip install html5lib' or install html5lib
	print(soup.prettify())



def main():
	get_page()
	#driver.close()


if __name__ == "__main__":
	main()
