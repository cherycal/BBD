__author__ = 'chance'

import sys

sys.path.append('../modules')
import pandas as pd
import push

inst = push.Push()

import sqldb
bdb = sqldb.DB('Baseball.db')

def main():
	url_text = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=0&type=8&season=2022&month=0&season1=2022&ind=0&team=0,ts&rost=0&age=0&filter=&players=0"

	print(url_text)



	csvfile = f"C:\\Users\\chery\\Documents\\BBD\\team_pitching_2022.csv"


	df = pd.read_html(url_text)[5]
	df.to_csv(csvfile, index=False)
	pass

	#print(f"{df}")


if __name__ == "__main__":
	main()
