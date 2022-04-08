__author__ = 'chance'
import sys
sys.path.append('../modules')
import fantasy
import inspect

from datetime import datetime
mode = "TEST"
fantasy = fantasy.Fantasy(mode)

def run_function(function):
    print("Function: " + str(inspect.stack()[-2].code_context))
    return


def main():

    ts = datetime.now()  # current date and time
    formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
    time6 = ts.strftime("%H%M%S")
    current_time = int(time6)
    print("Start at " + formatted_date_time)

    run_function(fantasy.get_db_player_info())


if __name__ == "__main__":
    main()