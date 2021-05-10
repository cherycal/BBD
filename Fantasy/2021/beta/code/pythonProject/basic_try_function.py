import pandas as pd
import numpy as np
import dataframe_image as dfi
import sys

sys.path.append('./modules')
import sqldb
import push
import fantasy
import time
import csv
from os import path
import random
from datetime import date, datetime
from datetime import timedelta
import tools
import os
from pathlib import Path
import inspect


plat = tools.get_platform()
print(plat)
push_instance = push.Push()
mode = "TEST"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')


# defining a decorator
def hello_decorator(func):
	# inner1 is a Wrapper function in
	# which the argument is called

	# inner function can access the outer local
	# functions like in this case "func"
	def inner1():
		print("Hello, this is before function execution")

		# calling the actual function now
		# inside the wrapper function.
		tries = 0
		max_tries = 3
		incomplete = 1
		while incomplete and tries < max_tries:
			try:
				func()
				incomplete = 0
			except Exception as ex:
				print(str(ex))
				#push_instance.push("Attempt failed", str(ex))
				tries += 1
				time.sleep(5)

		if tries == max_tries:
			print("Process failed: ")
			print(str(inspect.stack()))


		print("This is after function execution")

	return inner1

def tryfunc(func):
	print("Hello, this is before function execution")
	# calling the actual function now
	# inside the wrapper function.
	tries = 0
	max_tries = 1
	incomplete = 1
	while incomplete and tries < max_tries:
		try:
			func()
			incomplete = 0
		except Exception as ex:
			print(str(ex))
			#push_instance.push("Attempt failed", str(ex))
			tries += 1
			time.sleep(2)

	if tries == max_tries:
		print("Process failed: ")
		print(str(inspect.stack()))


	print("This is after function execution")


# defining a function, to be called inside wrapper
# def function_to_be_used():
#	push_instance()

def good_function():
	print("hello")
	names, c = bdb.select_w_cols("SELECT * FROM ESPNLeagues")
	# names = list(map(lambda x: x[0], c.description))
	print(names)
	for t in c:
		print(t)

def test_function():
	cmd = "SELECT * FROM ESPNLeagues"
	bdb.cursor.execute(cmd)
	bdb.conn.commit()

#run_function( print("HELLO WORLD !!") )

# passing 'function_to_be_used' inside the
# decorator to control its behavior


cmd = "SELECT * FROM ESPNLeagues"
tryfunc(test_function)
for row in bdb.cursor.fetchall():
	print(row)

bdb.close()
print("End")