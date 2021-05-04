import json
import os
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb, tools
import pickle
import os.path
from os import path
import push
import fantasy
import inspect
import traceback
import random
import operator
import pycurl
import certifi
import io
from io import BytesIO
import pandas as pd
import csv

def main():
	bdb = sqldb.DB('Baseball.db')

	csv_file_name = "C:\\Users\chery\Documents\BBD\AuctionValues.csv"

	with open(csv_file_name, newline='') as csvfile:
		csvdata = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in csvdata:
			#print(row)
			cmd = "INSERT INTO ESPNDrafts (Year,League,keeper,teamId,playerid,bidAmount) VALUES (" + ','.join(row) + ")"
			print(cmd)
			bdb.conn.execute(cmd)
			bdb.conn.commit()

	bdb.close()


if __name__ == "__main__":
	main()
