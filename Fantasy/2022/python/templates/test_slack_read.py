import os
import sys
import time

sys.path.append('../modules')

import fantasy
mode = "PROD"
fantasy = fantasy.Fantasy(mode, caller=os.path.basename(__file__))

import tools
process_instance = tools.Process()

process_name = "General"
while True:
    print(fantasy.read_slack())
    time.sleep(4)
    #ts = float('1694741871.190199')


# All of this has been replaced
# https://slack.dev/python-slack-sdk/
# import logging
# logging.basicConfig(level=logging.DEBUG)
#
#
# from slack_sdk.webhook import WebhookClient
#
# SLACK_URL_SUFFIX = os.environ.get('slack_url_suffix')
#
#
# slack_url = f"https://hooks.slack.com/services/{SLACK_URL_SUFFIX}"
# slack_webhook = WebhookClient(slack_url)
#
# response = slack_webhook.send(text="Hello!")
# assert response.status_code == 200
# assert response.body == "ok"
#

#
# # Enable debug logging
# import logging
# logging.basicConfig(level=logging.DEBUG)
# # Verify it works
# from slack_sdk import WebClient
# client = WebClient()
# api_response = client.api_test()
# print(api_response)