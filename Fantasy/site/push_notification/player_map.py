from __future__ import print_function

import csv
import io

import requests

headers={}
headers["User-Agent"]= "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0"
headers["DNT"]= "1"
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
headers["Accept-Encoding"] = "deflate"
headers["Accept-Language"]= "en-US,en;q=0.5"
lines = []

#file_id="1vXxl5fGbzlycn_8km47qq6byZ50mzhvPClpHMSheCVw"
file_id="1JgczhD5VDQ1EiXqVG-blttZcVwbZd5_Ne_mefUGwJnk"
url = "https://docs.google.com/spreadsheets/d/{0}/export?format=csv".format(file_id)

r = requests.get(url)

sio = io.StringIO( r.text, newline=None)
reader = csv.reader(sio, dialect=csv.excel)

rownum = 0
colnum = 0

for row in reader:
    while rownum < 1:
        for col in row:
            print(row[colnum] + ": " + str(colnum) )
            colnum +=1
        rownum += 1