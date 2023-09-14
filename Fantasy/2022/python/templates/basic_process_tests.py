import sys
sys.path.append('../modules')
import tools
import datetime

plat = tools.get_platform()
print(plat)
mode = "PROD"


# import time
# import logging
# import colorlog
# import inspect
# import sqlite3
# from datetime import date, timedelta
# import os


def main():
    process_instance = tools.Process()
    date8 = datetime.datetime.now().strftime("%Y%m%d")
    process_name = "RosterRun"
    # print(f'{process_instance.get_process()} - {date8}')
    # print(f"Process status for {process_name}: {process_instance.get_process_status(process_name)}")
    # process_instance.set_process_status(process_name, 1)
    print(f"Process status for {process_name}: {process_instance.get_process_status(process_name)}, "
          f"UpdateDate = {process_instance.get_process_date(process_name)} on {date8}")
    print(f"Is process UpdateDate today ? {process_instance.get_process_date(process_name) == date8}")
    if not process_instance.get_process_status(process_name) and \
            process_instance.get_process_date(process_name) == date8:
        print(f"Run roster suite")
        process_instance.set_process_status(process_name, 1)
    else:
        print(f"Don't run roster suite")



if __name__ == "__main__":
    main()


# All of this moved to the tools module
# def get_logger(logfilename='process_default.log',
#                logformat='%(asctime)s:%(levelname)s:%(funcName)s:%(lineno)d:%(message)s:%(pathname)s\n'):
#     bold_seq = '\033[1m'
#     colorlog_format = (
#         f'{bold_seq} '
#         '%(log_color)s '
#         f'{logformat}'
#     )
#     colorlog.basicConfig(format=colorlog_format)
#
#     logger_instance = logging.getLogger(__name__)
#     logger_instance.setLevel(logging.DEBUG)
#
#     formatter = logging.Formatter(logformat)
#     file_handler = logging.FileHandler(logfilename)
#     file_handler.setFormatter(formatter)
#     logger_instance.addHandler(file_handler)
#
#     return logger_instance
#
# def print_calling_function():
#     print('\n')
#     print("Printing calling information (fantasy.py)")
#     print("#############################")
#     # print(str(inspect.stack()[-2].filename) + ", " + str(inspect.stack()[-2].function) +
#     #      ", " + str(inspect.stack()[-2].lineno))
#     print(str(inspect.stack()[1].filename) + ", " + str(inspect.stack()[1].function) +
#           ", " + str(inspect.stack()[1].lineno))
#     # print(str(inspect.stack()[-1].filename) + ", " + str(inspect.stack()[-1].function) +
#     #      ", " + str(inspect.stack()[-1].lineno))
#     print("#############################")
#     return
#
# class Process(object):
#
#     def __init__(self, logger_instance=None):
#         self.db = f'C:\\Ubuntu\\Shared\\data\\Process.db'
#         self.conn = sqlite3.connect(self.db, timeout=15)
#         self.cursor = self.conn.cursor()
#         self.name = "process_instance"
#         if logger_instance is None:
#             logname = './logs/pushlog.log'
#             self.logger_instance = get_logger(logfilename=logname)
#         else:
#             self.logger_instance = logger_instance
#
#     def execute(self, cmd, verbose=0):
#         if verbose:
#             print_calling_function()
#         self.cursor.execute(cmd)
#         self.conn.commit()
#
#     def select(self, query, verbose=0):
#         if verbose:
#             print_calling_function()
#         self.cursor.execute(query)
#         self.conn.commit()
#         return self.cursor.fetchall()
#
#
#
#     def get_process(self):
#         return self.name
#
#     def set_process_status(self, calling_function, flag_):
#         if calling_function:
#             cmd = f"update ProcessStatus set ProcessStatus = {flag_} where ProcessName = '{calling_function}'"
#             self.logger_instance.info(cmd)
#             self.execute(cmd)
#             self.logger_instance.info(f"Successfully ProcessStatus to {flag_} for {calling_function}")
#             # self.push(title="ProcessStatus",
#             #           body=f"Successfully ProcessStatus to {flag_} for {calling_function}")
#
#         return
#
#     def get_process_status(self, calling_function=None):
#         status_flag = None
#         if calling_function:
#             cmd = f"select ProcessStatus from ProcessStatus where ProcessName = '{calling_function}'"
#             self.logger_instance.info(cmd)
#             d = self.select(cmd)
#             status_flag = d[0][0]
#         return status_flag
#
