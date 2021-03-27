import sys
from selenium import webdriver


# for webscraping

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
    msg = ""
    out_string = ""
    for i in in_list:
        if i[-1] == ":":
            out_string += i
        else:
            out_string += i + ", "
    out_string = out_string[:-2]
    out_string += '\n'
    return out_string
