__author__ = 'chance'

import inspect
import logging
import os
import smtplib
import sqlite3
import time
from datetime import datetime
from email.mime.text import MIMEText

import colorlog
import dataframe_image as dfi
import pandas as pd
import tweepy
# from pushbullet import PushBullet
from pyfcm import FCMNotification
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_api_token = os.environ["SLACK_BOT_TOKEN"]
slack_alerts_channel = os.environ["SLACK_ALERTS_CHANNEL"]
slack_requests_channel = os.environ["SLACK_CHANNEL"]
slack_client = WebClient(token=slack_api_token)

# TWITTER KEYS
APIKEY = os.environ.get('APIKEY')
APISECRETKEY = os.environ.get('APISECRETKEY')
ACCESSTOKEN = os.environ.get('ACCESSTOKEN')
ACCESSTOKENSECRET = os.environ.get('ACCESSTOKENSECRET')
SE = f"{os.environ.get('GMA')}@gmail.com"
SP = os.environ.get('GMPY')
SN = f"{str(int(os.environ.get('PN')) - 4)}@vtext.com"

# PUSHBUCKET
PBTOKEN = os.environ.get('PBTOKEN')

# SLACK ( DECOMMISSIONED 20230416 )
SLACK_URL_SUFFIX = os.environ.get('slack_url_suffix')

########################################################################################################################
REG_ID = os.environ.get('reg_id')
API_KEY = os.environ.get('api_key')


########################################################################################################################

def ordinal(n):
    if 10 <= n % 100 < 20:
        return str(n) + 'th'
    else:
        return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, "th")


def get_logger(logfilename='push_default.log',
               logformat='%(asctime)s:%(levelname)s:%(funcName)s:%(lineno)d:%(message)s:%(pathname)s\n'):
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


def print_calling_function():
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


def push_attachment(attachment, body="None"):
    res = False
    try:
        file_response = slack_client.files_upload_v2(
            channel=slack_alerts_channel,
            initial_comment=body,
            file=attachment,
            title=body
        )
        view_response = False
        if view_response:
            print(f"Response: {file_response}")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert f"Upload error {e.response['error']}"
    return res


def set_tweepy(self):
    api = tweepy.API(self.auth)
    return api


class Push(object):
    MAX_MSG_LENGTH: int

    def __init__(self, logger_instance=None):
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
        self.api = set_tweepy(self)
        self.tweet_count = 0
        # self.pb = PushBullet(PBTOKEN)
        self.slack_url = f"https://hooks.slack.com/services/{SLACK_URL_SUFFIX}"
        self.EMAIL_FROM = f"{os.environ.get('GMA')}@gmail.com"
        self.EMAIL_PASSWORD = os.environ.get('GMPY')
        self.EMAIL_TO = f"{str(int(os.environ.get('PN')) - 4)}@vtext.com"
        self.DEFAULT_SMS = f"{str(int(os.environ.get('PN')) - 4)}@vtext.com"
        self.send_message_flag = False
        self.db = f'C:\\Ubuntu\\Shared\\data\\Push.db'
        self.conn = sqlite3.connect(self.db, timeout=15)
        self.cursor = self.conn.cursor()

    def execute(self, cmd, verbose=0):
        if verbose:
            print_calling_function()
        self.cursor.execute(cmd)
        self.conn.commit()

    def select(self, query, verbose=0):
        if verbose:
            print_calling_function()
        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchall()

    def incr_tweet_count(self):
        self.tweet_count += 1
        return self.tweet_count

    def get_tweet_count(self):
        return self.tweet_count

    def push(self, body, title=None):
        res = 0
        SUPPRESS_FLAG = False
        if title is None:
            title = "No title provided"
        if not SUPPRESS_FLAG:
            message = f"{body}\r\n\r\n"
            try:
                response = slack_client.chat_postMessage(
                    channel=slack_alerts_channel,
                    text=message)
                view_response = False
                if view_response:
                    print(f"Response: {response}")
            except SlackApiError as e:
                # You will get a SlackApiError if "ok" is False
                assert e.response["error"]

            ANDROID = False
            if ANDROID:
                res = self.push_service.notify_single_device(registration_id=self.registration_id,
                                                             message_title=title,
                                                             message_body=body, sound="whisper.mp3",
                                                             badge="Test2")
        return res

    def set_send_message_flag(self, flag_, calling_function=None):
        self.send_message_flag = flag_
        if calling_function:
            cmd = f"update SMSflag set flag = {flag_} where Function = '{calling_function}'"
            self.logger_instance.info(cmd)
            self.execute(cmd)
            self.logger_instance.info(f"Successfully set_send_message_flag to {flag_} for {calling_function}")
            self.push(title="set_send_message_flag",
                      body=f"Successfully set_send_message_flag to {flag_} for {calling_function}")
        else:
            cmd = f"update SMSflag set flag = {flag_}"
            self.logger_instance.info(cmd)
            self.execute(cmd)
            self.logger_instance.info(f"Successfully set_send_message_flag to {flag_} for all")
            self.push(title="set_send_message_flag",
                      body=f"Successfully set_send_message_flag to {flag_} for all")
        return self.send_message_flag

    def get_send_message_flag(self, calling_function=None):
        if calling_function:
            cmd = f"select flag from SMSflag where Function = '{calling_function}'"
            self.logger_instance.info(cmd)
            d = self.select(cmd)
        else:
            cmd = f"select max(flag) from SMSflag"
            self.logger_instance.info(cmd)
            d = self.select(f"select max(flag) from SMSflag")
        send_message_flag = d[0][0]
        return "On" if send_message_flag else "Off"

    def get_twitter_api(self):
        return self.api

    def get_twitter_auth(self):
        return self.auth

    def send_message(self, message, subject="No subject given", calling_function=None, recipients=None):
        if not recipients:
            recipients = self.EMAIL_TO
        on_flag = self.get_send_message_flag(calling_function)
        print(f"send_message is set to {on_flag}")
        if on_flag == "On":
            try:
                EMAIL_FROM = f"{os.environ.get('GMA')}@gmail.com"
                PASSWORD = os.environ.get('GMPY')
                EMAIL_TO = recipients
                auth = (EMAIL_FROM, PASSWORD)

                AMPM_flag = datetime.now().strftime('%p')
                if AMPM_flag == "AM":
                    AMPM_flag = "A M"
                else:
                    AMPM_flag = "P M"
                # ordinal_day = ordinal(int(datetime.now().strftime('%#d')))
                msg = MIMEText(f"{message}, "
                               f"{datetime.now().strftime('%#I:%M')} {AMPM_flag}")
                ## f" on {datetime.now().strftime('%B')} {ordinal_day} ")
                msg['Subject'] = subject
                msg['From'] = EMAIL_FROM
                msg['To'] = EMAIL_TO

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(auth[0], auth[1])
                    server.set_debuglevel(2)
                    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
                    server.quit()
            except Exception as ex:
                print(f"Exception in push.send_message: {ex}")
        if calling_function == "GameData":
            time.sleep(10)
        else:
            time.sleep(2)
        return

    def login_sms_server(self):
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.EMAIL_TO, self.EMAIL_PASSWORD)
            server.set_debuglevel(1)

    def tweet(self, msg, PROCESS_FLAG=False):
        if PROCESS_FLAG:
            ts = datetime.now()  # current date and time
            formatted_date_time = ts.strftime("%I%M")
            # print(f'Msg:{msg},\nMsg length{len(msg)}\nMax length: {self.MAX_MSG_LENGTH}')
            if msg != "" and len(msg) < self.MAX_MSG_LENGTH:
                try:
                    self.api.update_status(msg + " " + str(len(msg)) + "-" + str(formatted_date_time))
                except Exception as ex:
                    print("try failed" + ": " + str(ex))
                    print_calling_function()
            else:
                while len(msg) < self.MAX_MSG_LENGTH:
                    trunc_msg = msg[0:self.MAX_MSG_LENGTH]
                    try:
                        self.api.update_status("Invalid msg" + " (" + str(formatted_date_time) + ")")
                        self.api.update_status(trunc_msg + " (" + str(formatted_date_time) + ")")
                    except Exception as ex:
                        print("try failed" + ": " + str(ex))
                        print_calling_function()
                    msg = msg[self.MAX_MSG_LENGTH:]
        return

    def tweet_media(self, img, msg, PROCESS_FLAG=False):
        self.incr_tweet_count()
        print(f"Current tweet count is {self.tweet_count}")
        if PROCESS_FLAG and self.tweet_count:
            ts = datetime.now()  # current date and time
            formatted_date_time = ts.strftime("%I%M%S.%f")[0:9]
            if len(msg) < self.MAX_MSG_LENGTH:
                # self.api.update_status(msg)
                try:
                    self.api.update_with_media(img, status=f"{msg} ({str(self.tweet_count)})")
                except Exception as ex:
                    print("try failed" + ": " + str(ex))
                    push(f"Error in tweet_media, Error: {str(ex)}")
                    print_calling_function()
            else:
                try:
                    self.api.update_status("Invalid msg" + " (" + str(formatted_date_time) + ")")
                except Exception as ex:
                    print("try failed" + ": " + str(ex))
                    print_calling_function()

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
                self.logger_instance.info(full_msg)
                self.push(title, full_msg)
                self.send_message(full_msg)
                # self.tweet(full_msg)
                time.sleep(1)
                full_msg = msg
                msg_len = len(full_msg)
            else:
                full_msg += str(msg)
        # Push the remainder out
        # full_msg += "\n\n-------\n\n"
        print("Message remainder:\n" + full_msg)
        self.logger_instance.info(full_msg)
        self.push(title, full_msg)
        self.send_message(full_msg)
        # self.tweet(full_msg)
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
            # self.push()
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
