import sys

sys.path.append('../modules')
import sqldb
import push
import tools

plat = tools.get_platform()
print(plat)
push_instance = push.Push()
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# Twitter KEYS ( see push module for usage )
# APIKEY = os.environ.get('APIKEY')
# APISECRETKEY = os.environ.get('APISECRETKEY')
# ACCESSTOKEN = os.environ.get('ACCESSTOKEN')
# ACCESSTOKENSECRET = os.environ.get('ACCESSTOKENSECRET')
# API_KEY = os.environ.get('api_key')
# REG_ID = os.environ.get('reg_id')

# tblname = 'ESPNRosters'
# bdb.table_to_csv(tblname)

push_instance.push("test push", f'test push')