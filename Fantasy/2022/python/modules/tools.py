import logging
import sys
import time
import traceback

import colorlog
from selenium import webdriver

import push

# DEBUG: Detailed information, typically of interest only when diagnosing problems.

# INFO: Confirmation that things are working as expected.

# WARNING: An indication that something unexpected happened,
# or indicative of some problem in the near future (e.g. ‘disk space low’).
# The software is still working as expected.

# ERROR: Due to a more serious problem, the software has not been able
# to perform some function.

# CRITICAL: A serious error, indicating that the program itself may be
# unable to continue running.

# for webscraping
# try:
# except Exception as ex:
#      print(str(ex))

push_instance = push.Push()

def get_logger(logfilename = 'test.log',
               logformat = '%(asctime)s:%(levelname)s'
                           ':%(funcName)s:%(lineno)d:%(message)s:%(pathname)s\n'):

    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{logformat}'
    )
    colorlog.basicConfig(format=colorlog_format)

    logger_instance = logging.getLogger(__name__)
    logger_instance.setLevel(logging.DEBUG)

    formatter = logging.Formatter(logformat)
    file_handler = logging.FileHandler(logfilename)
    file_handler.setFormatter(formatter)
    logger_instance.addHandler(file_handler)

    return logger_instance


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]

def get_driver(mode=""):
    platform = get_platform()
    options = webdriver.ChromeOptions()
    driver = ""
    if mode == "headless":
        options.add_argument('--headless')
    if platform == "Windows":
        driver = webdriver.Chrome('C:/Users/chery/chromedriver.exe', options=options)
    elif (platform == "linux") or (platform == "Linux"):
        driver = webdriver.Chrome('/usr/bin/chromedriver', options=options)
    else:
        print("Platform " + platform + " not recognized. Exiting.")
        exit(-1)
    return driver


def string_from_list(in_list):
    out_string = ""
    for i in in_list:
        if i[-1] == ":":
            out_string += i
        else:
            out_string += i + ", "
    out_string = out_string[:-2]
    out_string += '\n'
    return out_string

def tryfunc(func):
    tries = 0
    max_tries = 4
    incomplete = True
    while incomplete and tries < max_tries:
        try:
            func()
            incomplete = False
        except Exception as ex:
            print(str(ex))
            tries += 1
            time.sleep(.5)
            if tries == max_tries:
                print("Process failed: ")
                print("Exception in user code:")
                print("-" * 60)
                traceback.print_exc(file=sys.stdout)
                print("-" * 60)
                push_instance.push("Process failed:", f'Error: {ex}\nFunction: {func}')

def try_wrap(func):
    def tryfunction(*args, **kwargs):
        tries = 0
        max_tries = 3
        while tries < max_tries:
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print(str(ex))
                # push_instance.push("Attempt failed", str(ex))
                tries += 1
                time.sleep(2)
        if tries == max_tries:
            print("Process failed: ")
            print("Exception in user code:")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)

    return tryfunction
