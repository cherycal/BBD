import sys

sys.path.append('../modules')
import sqldb
import re

bdb = sqldb.DB('Baseball.db')
r = bdb.select_plus(f"SELECT name FROM ESPNPlayerDataCurrent")
for d in r['rows']:
    word = d[0]
    if re.search("[A-Z]\.|Jr\.", word):
        print(f"FOUND {word}")
    else:
        pass
        #print(f"No {word}")