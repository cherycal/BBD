__author__ = 'chance'

import inspect
import logging
import os
import smtplib
import time
from datetime import datetime

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
SN = f"{str(int(os.environ.get('PN'))-4)}@vtext.com"

# PUSHBUCKET
PBTOKEN = os.environ.get('PBTOKEN')

# SLACK ( DECOMMISSIONED 20230416 )
SLACK_URL_SUFFIX = os.environ.get('slack_url_suffix')

########################################################################################################################
REG_ID = os.environ.get('reg_id')
API_KEY = os.environ.get('api_key')


########################################################################################################################

def get_logger(logfilename='push_default.log',
               logformat='%(asctime)s:%(levelname)s'
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
        self.tweet_count = 0
        # self.pb = PushBullet(PBTOKEN)
        self.slack_url = f"https://hooks.slack.com/services/{SLACK_URL_SUFFIX}"
        self.se = SE
        self.sp = SP
        self.sn = SN
        self.sms_auth = (self.se, self.sp)

    def incr_tweet_count(self):
        self.tweet_count += 1
        return self.tweet_count

    def get_tweet_count(self):
        return self.tweet_count

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
        res = 0
        SUPPRESS_FLAG = False
        if not SUPPRESS_FLAG:
            message = f"{body}\r\n\r\n"

            try:
                response = slack_client.chat_postMessage(
                    channel=slack_alerts_channel,
                    text=message
                )
            except SlackApiError as e:
                # You will get a SlackApiError if "ok" is False
                assert e.response["error"]  # st

            # All slack data
            # slack_data = {
            #     "channel": "alerts",
            #     "username": "AlertsBaseball",
            #     "attachments": [
            #         {
            #             "color": "#FF0000",
            #             "title": body,
            #             "fields": [
            #                 {
            #                     "title": title,
            #                     "value": message,
            #                     "short": True,
            #                 }
            #             ]
            #         }
            #     ]
            # }
            # byte_length = str(sys.getsizeof(slack_data))
            # headers = {'Content-Type': "application/json",
            #            'Content-Length': byte_length}
            #
            # # Posting requests after dumping the slack data
            # response = requests.post(self.slack_url, data=json.dumps(slack_data), headers=headers)
            #
            # # Post request is valid or not!
            # if response.status_code != 200:
            #     raise Exception(response.status_code, response.text)

            # push to android device
            ANDROID = False
            if ANDROID:
                res = self.push_service.notify_single_device(registration_id=self.registration_id,
                                                             message_title=title,
                                                             message_body=body, sound="whisper.mp3",
                                                             badge="Test2")
            # self.pb.push_note(title, body)
        return res

    def push_attachment(self, attachment, body="None"):
        res = False
        try:
            file_response = slack_client.files_upload_v2(
                channel=slack_alerts_channel,
                initial_comment=body,
                file=attachment,
                title=body
            )
            file_url = file_response["file"]["permalink"]
            text = f"{body}: {file_url}"
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert f"Upload error {e.response['error']}"

        # try:
        #     response = slack_client.chat_postMessage(
        #         channel=slack_alerts_channel,
        #         text=text,
        #         blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
        #     )
        #     #print(f"Slack response: {response}")
        # except SlackApiError as e:
        #     # You will get a SlackApiError if "ok" is False
        #     assert f"Post error {e.response['error']}"
        return res

    def get_twitter_api(self):
        return self.api

    def get_twitter_auth(self):
        return self.auth

    def send_message(self, message):
        message = f"\r\n{message}"
        recipient = self.sn
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sms_auth[0], self.sms_auth[1])
            server.sendmail(self.sms_auth[0], recipient, message)
        except Exception as ex:
            print(f"Exception in push.send_message: {ex}")
        return

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
                self.logger_instance.info(full_msg)
                self.push(title, full_msg)
                self.send_message(full_msg)
                #self.tweet(full_msg)
                time.sleep(1)
                full_msg = msg
                msg_len = len(full_msg)
            else:
                full_msg += str(msg)
        # Push the remainder out
        #full_msg += "\n\n-------\n\n"
        print("Message remainder:\n" + full_msg)
        self.logger_instance.info(full_msg)
        self.push(title, full_msg)
        self.send_message(full_msg)
        #self.tweet(full_msg)
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
