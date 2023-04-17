import sys

sys.path.append('./modules')
import sqldb

#plat = tools.get_platform()
#print(plat)
#push_instance = push.Push()
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

tables = ['UpcomingStartsWithStats','SD_FRAN','ACheck_ID','ACheck_Statcast','AllSplits','TeamSplits','RunningTotalsPitching_FRAN',
          'SituationalEventsRosters','AddDrops']

for tbl in tables:
    try:
        bdb.table_to_csv(tbl)
    except Exception as ex:
        print(f'Error in table_to_csv {tbl}: {ex}')
