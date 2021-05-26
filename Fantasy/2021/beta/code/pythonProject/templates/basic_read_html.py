__author__ = 'chance'

import sys

sys.path.append('../modules')
import pandas as pd
import time
import push

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
