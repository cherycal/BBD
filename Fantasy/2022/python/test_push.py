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

print(f'Hello world')

#push_instance.push("Title 101", f'MSG 101')
push_instance.tweet_media("image2.png", f'Table', True)

print(f'Bye bye')