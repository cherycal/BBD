__author__ = 'chance'

import os
import smtplib

# CARRIERS = {
#     "att": "@mms.att.net",
#     "tmobile": "@tmomail.net",
#     "verizon": "@vtext.com",
#     "sprint": "@messaging.sprintpcs.com"
# }

# EMAIL = "ccrlyclhn@gmail.com"
# PASSWORD = "snnlcxshaffvyfjv"

EMAIL = f"{os.environ.get('GMA')}@gmail.com"
PASSWORD = os.environ.get('GMPY')
NUM = f"{str(int(os.environ.get('PN'))-4)}@vtext.com"

def send_message(recipient, message):
    auth = (EMAIL, PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)


if __name__ == "__main__":
    send_message(NUM, "pymessage22")