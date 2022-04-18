__author__ = 'chance'

import sys

sys.path.append('../modules')

import fantasy
import os


fantasy = fantasy.Fantasy(caller=os.path.basename(__file__))

def main():
	name = "HernÃ¡ndez, CÃ©sar"
	#name = unicodedata.normalize('NFKD', name)
	print(name.encode("latin-1").decode("utf-8"))




if __name__ == "__main__":
	main()
