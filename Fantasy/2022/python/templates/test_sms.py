__author__ = 'chance'

import datetime
import os
import smtplib
from email.mime.text import MIMEText


# CARRIERS = {
#     "att": "@mms.att.net",
#     "tmobile": "@tmomail.net",
#     "verizon": "@vtext.com",
#     "sprint": "@messaging.sprintpcs.com"
# }

# EMAIL = "ccrlyclhn@gmail.com"
# PASSWORD = "snnlcxshaffvyfjv"
#
# EMAIL = f"{os.environ.get('GMA')}@gmail.com"
# PASSWORD = os.environ.get('GMPY')
# NUM = f"{str(int(os.environ.get('PN')) - 4)}@vtext.com"
#

def send_message(message, subject):
    FROM_ADDR = f"{os.environ.get('GMA')}@gmail.com"
    PASSWORD = os.environ.get('GMPY')
    TO_ADDR = f"{str(int(os.environ.get('PN')) - 4)}@vtext.com"
    auth = (FROM_ADDR, PASSWORD)

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = FROM_ADDR
    msg['To'] = TO_ADDR

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(auth[0], auth[1])
        server.set_debuglevel(1)
        server.sendmail(FROM_ADDR, TO_ADDR, msg.as_string())
        server.quit()


if __name__ == "__main__":
    send_message(f"pymessage22: {datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}",
                 f"Test subject at {datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}")
