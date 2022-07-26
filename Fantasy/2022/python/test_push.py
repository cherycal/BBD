import sys

sys.path.append('./modules')
import sqldb
import push

#plat = tools.get_platform()
#print(plat)
push_instance = push.Push()
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

push_instance.push("Test", f'test')