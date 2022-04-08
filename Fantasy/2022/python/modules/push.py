__author__ = 'chance'

import inspect
import logging
import os
import time
from datetime import datetime

import colorlog
import dataframe_image as dfi
import pandas as pd
import tweepy
from pyfcm import FCMNotification

# APP ID: 20456708

APIKEY = os.environ.get('APIKEY')
APISECRETKEY = os.environ.get('APISECRETKEY')
ACCESSTOKEN = os.environ.get('ACCESSTOKEN')
ACCESSTOKENSECRET = os.environ.get('ACCESSTOKENSECRET')
API_KEY = os.environ.get('api_key')
REG_ID = os.environ.get('reg_id')

def get_logger(logfilename = 'push_default.log',
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

def set_tweepy(self, *args, **kwargs):
    api = tweepy.API(self.auth)
    return api

class Push(object):
    MAX_MSG_LENGTH: int
    def __init__(self, logger_instance=None, *args, **kwargs):
        api_key = API_KEY
        reg_id = REG_ID
        self.push_service = FCMNotification(api_key=api_key)
        self.registration_id = reg_id
        self.message_title = "Python test 1"
        self.message_body = "Hello python test 1"
        self.res = {}
        self.interval = 0
        self.title = None
        self.body = None
        self.MAX_MSG_LENGTH = 225
        self.str = ""
        self.auth = tweepy.OAuthHandler(APIKEY, APISECRETKEY)
        self.auth.set_access_token(ACCESSTOKEN, ACCESSTOKENSECRET)
        if logger_instance is None:
            logname = './logs/pushlog.log'
            self.logger_instance = get_logger(logfilename=logname)
        else:
            self.logger_instance = logger_instance

        # Create API object
        self.api = set_tweepy(self, *args, **kwargs)


    def print_calling_function(self):
        print('\n')
        print("Printing calling information (fantasy.py)")
        print("#############################")
        # print(str(inspect.stack()[-2].filename) + ", " + str(inspect.stack()[-2].function) +
        #      ", " + str(inspect.stack()[-2].lineno))
        print(str(inspect.stack()[1].filename) + ", " + str(inspect.stack()[1].function) +
              ", " + str(inspect.stack()[1].lineno))
        # print(str(inspect.stack()[-1].filename) + ", " + str(inspect.stack()[-1].function) +
        #      ", " + str(inspect.stack()[-1].lineno))
        print("#############################")
        return

    def push(self, title="None", body="None"):
        res = self.push_service.notify_single_device(registration_id=self.registration_id,
                                                     message_title=title,
                                                     message_body=body, sound="whisper.mp3",
                                                     badge="Test2")
        return res

    def get_twitter_api(self):
        return self.api

    def get_twitter_auth(self):
        return self.auth


    def tweet(self, msg):
        ts = datetime.now()  # current date and time
        formatted_date_time = ts.strftime("%I%M")
        # print(f'Msg:{msg},\nMsg length{len(msg)}\nMax length: {self.MAX_MSG_LENGTH}')
        if msg != "" and len(msg) < self.MAX_MSG_LENGTH:
            try:
                self.api.update_status(msg + " " + str(len(msg)) + "-" + str(formatted_date_time))
            except Exception as ex:
                print("try failed" + ": " + str(ex))
                self.print_calling_function()
        else:
            while len(msg) < self.MAX_MSG_LENGTH:
                trunc_msg = msg[0:self.MAX_MSG_LENGTH]
                try:
                    self.api.update_status("Invalid msg" + " (" + str(formatted_date_time) + ")")
                    self.api.update_status(trunc_msg + " (" + str(formatted_date_time) + ")")
                except Exception as ex:
                    print("try failed" + ": " + str(ex))
                    self.print_calling_function()
                msg = msg[self.MAX_MSG_LENGTH:]
        return

    def tweet_media(self, img, msg):
        ts = datetime.now()  # current date and time
        formatted_date_time = ts.strftime("%I%M%S.%f")[0:9]
        if len(msg) < self.MAX_MSG_LENGTH:
            # self.api.update_status(msg)
            try:
                self.api.update_with_media(img, status=msg + " (" + str(formatted_date_time) + ")")
            except Exception as ex:
                print("try failed" + ": " + str(ex))
                self.print_calling_function()
        else:
            try:
                self.api.update_status("Invalid msg" + " (" + str(formatted_date_time) + ")")
            except Exception as ex:
                print("try failed" + ": " + str(ex))
                self.print_calling_function()

        return

    def push_list(self, push_list, title="None"):
        max_msg_len = self.MAX_MSG_LENGTH
        msg_len = 0
        full_msg = ""
        for msg in push_list:
            msg_len += len(msg)
            # print("Msg: "+ msg)
            # print(msg_len)
            if msg_len > max_msg_len:
                print("Message part:\n" + full_msg)
                self.push(title, full_msg)
                self.tweet(full_msg)
                time.sleep(2.5)
                full_msg = msg
                msg_len = len(full_msg)
            else:
                full_msg += str(msg)
        # Push the remainder out
        print("Message remainder:\n" + full_msg)
        self.logger_instance.info(full_msg)
        self.push(title, full_msg)
        self.tweet(full_msg)
        return

    def push_list_twtr(self, push_list, title="None"):
        max_msg_len = self.MAX_MSG_LENGTH
        msg_len = 0
        full_msg = ""
        for msg in push_list:
            msg_len += len(msg)
            full_msg += str(msg)
        if msg_len > max_msg_len:
            index = [""] * len(push_list)
            col_headers = [""]
            df = pd.DataFrame(push_list, columns=col_headers, index=index)
            img = "mytable.png"
            dfi.export(df, img)
            self.tweet_media(img, title)
            #self.push()
        else:
            self.push(title, full_msg)
            self.tweet(full_msg)
        return

    def set_msg(self, title, body):
        self.title = title
        self.body = body

    def set_interval(self, interval):
        self.interval = interval

    def push_number(self, number):
        for i in range(0, number):
            self.push(self.title, self.body)
            time.sleep(4)

    def push_change(self, number, title="None", body="None"):
        self.title = title
        self.body = body
        if number < 0:
            self.push_number(1)
        elif number > 0:
            self.push_number(2)

        time.sleep(10)

        if abs(number) < 6000:
            self.push_number(int((abs(number) + 1) / 2))

    def string_from_list(self, in_list):
        s = ""
        for i in in_list:
            s += str(i)
            s += " "

        s = s[:-1]
        s += '\n'
        self.str = s
        return self.str