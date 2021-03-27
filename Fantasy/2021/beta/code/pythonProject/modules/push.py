__author__ = 'chance'

from pyfcm import FCMNotification
import time
from datetime import datetime
import tweepy

# APP ID: 20456708

APIKEY = "xFROaRKqUGekYP7XtybD5SKic"

APISECRETKEY = "9qQGFm27JDOCJtMs3SnlBPRhOeAv28ujqy6qXoUbB8t8q1zeQr"

ACCESSTOKEN = "1375606437410299905-47aXO2g5nwt5K0p1Qw69iVKJ5Mz4wN"

ACCESSTOKENSECRET = "pF84t0Xukgaaf4QL6khVTuBjsLBMdfH0ibuJSGa0CdUnr"


class Push(object):
    MAX_MSG_LENGTH: int

    # message_body: str

    def __init__(self):
        api_key = "AAAARAUK_1U:APA91bEWDFmhqWVEicI1xWh7R41lB8DGyjiRrLlfaa" \
                  "-CqLtMLvbGzLtL6nCBYgXVKKuiLas8hsX6YnHFQUoWqHZS_crAssz2B" \
                  "-msCzOAYqWqsTuc9AgPnTJL0OtPnEjBG9FC4hFd9339"
        reg_id = "fyOoafoZVl8:APA91bHk3CwpzBXTKbEZiFs6i57NZqnSDPrkA0vZI" \
                 "-rUbMmK6t1ov9bhqFULtLOUAfi0BXs0y4VCoRiu1nBdo82NK7iDCcIkMnV7eqpTDOP3a9X3bmMCPb4gk0OSIGPl5UANaOKFQjNl"
        self.push_service = FCMNotification(api_key=api_key)
        self.registration_id = reg_id
        self.message_title = "Python test 1"
        self.message_body = "Hello python test 1"
        self.res = {}
        self.interval = 0
        self.title = None
        self.body = None
        self.MAX_MSG_LENGTH = 240
        self.str = ""
        self.auth = tweepy.OAuthHandler(APIKEY, APISECRETKEY)
        self.auth.set_access_token(ACCESSTOKEN, ACCESSTOKENSECRET)

        # Create API object
        self.api = tweepy.API(self.auth)

    def push(self, title="None", body="None"):
        res = self.push_service.notify_single_device(registration_id=self.registration_id,
                                                     message_title=title,
                                                     message_body=body, sound="whisper.mp3",
                                                     badge="Test2")
        return res

    def tweet(self, msg):

        ts = datetime.now()  # current date and time
        formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
        if msg != "" and len(msg) < self.MAX_MSG_LENGTH - len(formatted_date_time) - 3:
            self.api.update_status(msg + " (" + str(formatted_date_time) + ")")
        else:
            self.api.update_status("Invalid msg")
        return

    def tweet_media(self, img, msg):
        ts = datetime.now()  # current date and time
        formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
        if msg != "" and len(msg) < self.MAX_MSG_LENGTH - len(formatted_date_time) - 1:
            # self.api.update_status(msg)
            self.api.update_with_media(img, status=msg + " (" + str(formatted_date_time) + ")")
        else:
            self.api.update_status("Invalid msg")

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
                time.sleep(2.5)
                full_msg = msg
                msg_len = len(full_msg)
            else:
                full_msg += str(msg)
        # Push the remainder out
        print("Message remainder:\n" + full_msg)
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
