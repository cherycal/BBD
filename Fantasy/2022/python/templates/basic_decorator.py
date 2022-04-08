import sys

sys.path.append('../modules')
import sqldb
import push
import time
import tools
import traceback
import fantasy
import os

plat = tools.get_platform()
print(plat)
push_instance = push.Push()
mode = "TEST"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

fantasy = fantasy.Fantasy(mode, caller=os.path.basename(__file__))


# def trywrap(func):
#     tries = 0
#     max_tries = 4
#     incomplete = True
#     while incomplete and tries < max_tries:
#         try:
#             func()
#             incomplete = False
#         except Exception as ex:
#             print(str(ex))
#             tries += 1
#             time.sleep(.5)
#             if tries == max_tries:
#                 print("Process failed: ")
#                 print("Exception in user code:")
#                 print("-" * 60)
#                 traceback.print_exc(file=sys.stdout)
#                 print("-" * 60)
#                 inst.push("Attempt failed:", f'Error: {ex}\nFunction: {func}')

def try_wrap(func):
    def tryfunc(*args, **kwargs):
        tries = 0
        max_tries = 3
        while tries < max_tries:
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print(str(ex))
                # push_instance.push("Attempt failed", str(ex))
                tries += 1
                time.sleep(5)

        if tries == max_tries:
            print("Process failed: ")
            print("Exception in user code:")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)

    return tryfunc


@try_wrap
def run_query(cmd):
    names, c = bdb.select_w_cols(cmd)
    print(names)
    for t in c:
        print(t)


#run_query("select * from ESPNLeague")

fantasy.tweet_daily_schedule()

bdb.close()
