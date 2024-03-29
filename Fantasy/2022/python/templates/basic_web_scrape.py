__author__ = 'chance'

import sys

sys.path.append('../modules')

from bs4 import BeautifulSoup as bs
import tools
import time

sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")

msg = ""

def get_page():
	url = "https://fantasy.espn.com/baseball/watchlist?leagueId=2692"
	print("url is: " + url)

	driver.get(url)
	time.sleep(sleep_interval)
	html = driver.page_source
	soup = bs(html, "html.parser")
	print(soup)




def main():
	get_page()
	driver.close()


if __name__ == "__main__":
	main()
