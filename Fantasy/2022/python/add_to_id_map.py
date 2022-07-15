import sys

sys.path.append('./modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

idmapcols, idmaprows = bdb.select_w_cols("select * from IDMap")
# print(idmapcols)
numcols = len(idmapcols)
nulls = ['NULL'] * numcols

cols, rows = bdb.select_w_cols("select * from AddToIDMap")
# print(cols)
lol = list()

for row in rows:
	[name, mlbid, espnid, injuryStatus, primaryPosition, eligiblePositions, throws, bats, mlbTeam] = row
	# print([name, mlbid, espnid, injuryStatus, primaryPosition, eligiblePositions, throws, bats, mlbTeam])
	insert_list = nulls.copy()
	target = [espnid, mlbid, name, name, name, injuryStatus, throws, bats, primaryPosition, mlbTeam, eligiblePositions]
	pos = [18, 10, 1, 11, 19, 42, 27, 26, 7, 5, 40]
	for x, y in zip(pos, target):
		insert_list[x] = y
	insert_list[0] = mlbid
	insert_tuple = tuple(insert_list)
	lol.append(insert_tuple)

for row in lol:
	print(row)

if len(lol):
	bdb.insert_many("IDMap", lol)

# UPDATE IDMAP
# set IDFANGRAPHS = FGID
# from (
# SELECT S.MLBID as MLBID,F.player as FGNAME, F.playerid as FGID, I.IDFANGRAPHS, I.FANGRAPHSNAME from StatcastUniverse2022 S
# LEFT OUTER JOIN IDMap I
# ON S.mlbid = I.mlbid
# left outer join FGCurrentUniverse F
# ON name = player
# WHERE
# IDFANGRAPHS = "NULL" and FGID not NULL
# ) as FG
# where IDMAP.MLBID = FG.MLBID