__author__ = 'chance'

import sys

sys.path.append('../modules')

import fantasy
import os

fantasy = fantasy.Fantasy(caller=os.path.basename(__file__))

def main():
	pass



if __name__ == "__main__":
	main()
