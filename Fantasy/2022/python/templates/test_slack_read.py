import sys

sys.path.append('./modules')

# https://slack.dev/python-slack-sdk/
import logging
logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk.webhook import WebhookClient

SLACK_URL_SUFFIX = os.environ.get('slack_url_suffix')


slack_url = f"https://hooks.slack.com/services/{SLACK_URL_SUFFIX}"
slack_webhook = WebhookClient(slack_url)

response = slack_webhook.send(text="Hello!")
assert response.status_code == 200
assert response.body == "ok"


#
# # Enable debug logging
# import logging
# logging.basicConfig(level=logging.DEBUG)
# # Verify it works
# from slack_sdk import WebClient
# client = WebClient()
# api_response = client.api_test()
# print(api_response)