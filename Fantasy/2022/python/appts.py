__author__ = 'chance'

import sys
from datetime import datetime

sys.path.append('./modules')

import random
from bs4 import BeautifulSoup as bs
import tools
import time
import push

inst = push.Push()
sleep_interval = 1
# Selenium
driver = tools.get_driver("headless")

msg = ""

def get_page():
	url = "https://www.sandiegocounty.gov/content/sdc/hhsa/" \
	      "programs/phs/community_epidemiology/dc/2019-nCoV/" \
	      "vaccines/vax-schedule-appointment.html#coronado"
	print("url is: " + url)

	driver.get(url)
	time.sleep(sleep_interval)
	html = driver.page_source
	soup = bs(html, "html.parser")
	results = soup.find_all('div',{"class": ["table parbase section","text parbase section"]})

	a_flag = 0
	b_flag = 0
	dates = 0
	avail = 0
	msg = ""

	for i in results:
		tds = i.find_all('td')
		j = i.find_all('b')
		for k in j:
			if k.find_all('a'):
				a = k.find_all('a',{"id": "coronado"})
				b = k.find_all('a',{"id": "southbayInstructions"})
				if len(a):
					#print(k)
					a_flag = 1
					continue
		if(a_flag):
			b_flag = 1
			a_flag = 0
			continue
		if(b_flag):
			lines = i.get_text().split('\n')
			for line in lines:
				#print("Line: " + line)
				msg += line
				msg += '\n'
				if line.find("March") > 0:
					#print("Date found")
					dates += 1
				if line.find("No appointments") > 0:
					#print("No appts")
					avail += 1
			b_flag = 0

	print("Dates found: " + str(dates))
	print("Available: " + str(avail))

	title = ""
	if( avail > 2):
		title = "AVAILABLE APPTS"
	else:
		title = "NO APPTS YET"

	inst.push(title, msg)
		

def main():
	count = 0
	hrs = 10
	while(count < 4 * hrs ):
		get_page()
		num1 = random.randint(10*60, 45*60)
		now = datetime.now()
		current_time = now.strftime("%I:%M:%S")
		print("Current Time =", current_time)
		print("Sleep for " + str(num1) + " seconds")
		time.sleep(num1)
		count += 1
	driver.close()


if __name__ == "__main__":
	main()
