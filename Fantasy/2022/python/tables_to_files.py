import sys

sys.path.append('./modules')
import sqldb
import tools

mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# tables = ['UpcomingStartsWithStats','SD_FRAN','AllSplits','TeamSplits','RunningTotalsPitching_FRAN',
#           'SituationalEventsRosters','AddDrops']

def run_tables():
    tables = ['ESPNRosters','UpcomingStartsWithStats','TeamSplits']
    for tbl in tables:
        bdb.table_to_csv(tbl)


@tools.try_wrap
def run_all_tables():
    tables = ['ESPNRosters','UpcomingStartsWithStats','TeamSplits','SituationalEventsRosters']
    for tbl in tables:
        bdb.table_to_csv(tbl)

@tools.try_wrap
def main():
    run_all_tables()


if __name__ == "__main__":
    main()
