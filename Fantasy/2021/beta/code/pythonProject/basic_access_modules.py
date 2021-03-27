__author__ = 'chance'

import sys
sys.path.append('./modules')

import fantasy

mode = "TEST"

fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()

# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')

rows = bdb.select("SELECT sql FROM sqlite_master WHERE tbl_name = 'ESPNLeagues' AND type = 'table'")
print()
print("Rows:")
for row in rows:
    print(row)

print()

rows = bdb.select("SELECT * FROM ESPNLeagues")

print()
print("Rows:")
for row in rows:
    print(row)

bdb.close()
