import sys

sys.path.append('./modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

idmapcols, idmaprows = bdb.select_w_cols("select * from IDMap")
print(idmapcols)
# numcols = len(idmapcols)
# nulls = ['NULL'] * numcols

result = bdb.select_plus("select * from ACheck_ID")
print(result['dicts'])
lol = list()
