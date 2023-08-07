import os
import sys

sys.path.append('../modules')
import sqldb
import push
import tools
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_api_token = os.environ["SLACK_BOT_TOKEN"]
slack_alerts_channel = os.environ["SLACK_ALERTS_CHANNEL"]
slack_client = WebClient(token=slack_api_token)


plat = tools.get_platform()
print(plat)
push_instance = push.Push()
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

def push_attachment(attachment, body="None"):
    res = False
    try:
        file_response = slack_client.files_upload_v2(
            channel=slack_alerts_channel,
            initial_comment=body,
            file=attachment,
        )
        file_url = file_response["file"]["permalink"]
        text = f"{body}: {file_url}"
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert f"Upload error {e.response['error']}"

    try:
        response = slack_client.chat_postMessage(
            channel=slack_alerts_channel,
            text=text,
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
        )
        #print(f"Slack response: {response}")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert f"Post error {e.response['error']}"
    return res


push_attachment("./mytable.png", "test push alerts")