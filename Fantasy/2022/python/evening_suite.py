import sys
sys.path.append('./modules')
import push
import sqldb
bdb = sqldb.DB('Baseball.db')

inst = push.Push()

scripts = ['odds.py','espn_daily_scoring_to_db.py',
           'savant_boxscores.py','fangraphs_universe.py']

for script in scripts:
    print(f'Trying script: {script}')
    try:
        exec(open(script).read())
        print(f'Script {script} succeeded')
    except Exception as ex:
        print(f'Script {script} failed with error {ex}')
        inst.push("Morning suite process error:", f'Error: {ex}\nFunction: {script}')

bdb.table_to_csv('UpcomingStartsWithStats')
#
#
# exec(open('odds.py').read())
# time.sleep(4)
# exec(open('espn_daily_scoring_to_db.py').read())
# time.sleep(4)
# exec(open('savant_boxscores.py').read())
# time.sleep(4)
# exec(open('fangraphs_universe.py').read())
