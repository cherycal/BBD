__author__ = 'chance'

import tools
from bs4 import BeautifulSoup
import time
import push
from git import Repo
from datetime import datetime
#import html
from html import HTML

def html_line(text,plus=0):
    h = HTML()
    p = ""
    if(plus):
        p = plus
    h.p(str(text)+p)
    f.write(str(h))

def html_hr():
    h = HTML()
    f.write(str(h.hr))



inst = push.Push()

sleep_interval = 8

url = "https://www.stubhub.com/the-strokes-tickets-the-strokes-inglewood-the-forum-los-angeles-3" \
      "-14-2020/event/104567878/?sliderMax=203.84%2C34.92&qty=2&sort=quality%20desc%2Cprice%20asc&sortKey=bestSeats&excl=1"

gitfile_name = "site/mobile/stub.html"
outfile_name = "/media/sf_Shared/first/site/mobile/stub.html"

h = HTML()
html_head = "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Stub</title><link href='stub.css' rel='stylesheet' type='text/css'></head><body><hr>"
html_footer = "</body></html>"

repo = Repo("/media/sf_Shared/first")
assert not repo.bare
git = repo.git

flag = 0


while (1):

    now = datetime.now()  # current date and time
    date_time = now.strftime("%m/%d/%Y-%H:%M:%S")

    f = open(outfile_name, "w")
    f.write(html_head)

    px_flag = 0

    try:

        driver = tools.get_driver()
        driver.get(url)
        time.sleep(sleep_interval)

        html = driver.page_source

        soup = BeautifulSoup(html,'html.parser')

        for div in soup.find_all('div', class_='RoyalTicketListPanel__column'):
            for h1 in div.find_all('h1'):
                flag = 0
                section = h1.text
                section_name = section.split()
                len_sec_num = len(section_name)
                section_short = section_name[len_sec_num-1]
                if(section_short.isnumeric()):
                    section_number = int(section_short)
                    if( (section_number >= 108 and section_number <= 113 ) or (section_number < 4) or (
                            section_number >= 124 and section_number <= 129 )):
                        flag = 1
                        print(section_short)
                        html_line(section_short,": ")

                        break
                else:
                    flag = 1
                    print(section_short)
                    html_line(section_short,": ")
                    break

            for px in div.find_all('div', class_='PriceDisplay__price'):
                if(flag):
                    px_flag = 1
                    print(px.text)
                    html_line(px.text)
                    html_hr()


        print(date_time)
        html_line(date_time)
        f.write("<img src='the-forum.jpg'>")
        f.write(html_footer)
        f.close()

        if (px_flag):
            git.add(gitfile_name)
            time.sleep(sleep_interval)
            git.commit('-m','update',gitfile_name)
            time.sleep(sleep_interval)
            git.push()
        else:
            print("No push")

        time.sleep(sleep_interval)
        driver.quit()
        time.sleep(40)

    except:
        print ("Get page failed ")
        driver.quit()
        time.sleep(40)
