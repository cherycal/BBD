import sys
from selenium import webdriver

#for webscraping

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
    if (mode == "headless"):
        options.add_argument('--headless')
    if (platform == "Windows"):
        driver = webdriver.Chrome('C:/Users/chery/chromedriver.exe', options=options)
    elif (platform == "linux") or (platform == "Linux"):
        driver = webdriver.Chrome('/usr/bin/chromedriver',options=options)
    else:
        print("Platform " + platform + " not recognized. Exiting.")
        exit(-1)
    return driver