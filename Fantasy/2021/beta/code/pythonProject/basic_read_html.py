__author__ = 'chance'

import json
import os
import sys
import time
import urllib.request
from datetime import datetime
import pandas as pd

sys.path.append('./modules')
from bs4 import BeautifulSoup
import requests
import pandas as pd
import tools
import time
import push
from datetime import timedelta, datetime, date

inst = push.Push()

import sqldb
bdb = sqldb.DB('Baseball.db')

def main():
	url_text = ""

	print(url_text)

	print("sleeping ....")
	time.sleep(1)

	csvfile = "C:\\Users\\chery\\Documents\\BBD\\FG\\" + bpdir + "\\" + "events_daily.csv"

	df = pd.read_html(url_text)[0]
	df.to_csv(csvfile, index=False)


	print("done")


if __name__ == "__main__":
	main()
