import json
import sys

import requests

sys.path.append('./modules')
import sqldb
import push
import os
#plat = tools.get_platform()
#print(plat)
push_instance = push.Push()
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')


if __name__ == '__main__':
    # Webhooks URL
    SLACK_URL_SUFFIX = os.environ.get('slack_url_suffix')

    url = f"https://hooks.slack.com/services/{url_suffix}"

    # Message you wanna send
    message = f'test slack push 4'

    # Title
    title = f'test slack title 4'

    # All slack data
    slack_data = {
        "channel": "alerts",
        "username": "AlertsBaseball",
        "attachments": [
            {
                "color": "#FF0000",
                "title": title,
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": True,

                    }
                ]
            }
        ]
    }

    slack_data2 = {
    "channel": "alerts",
    "attachments": [
        {
	        "mrkdwn_in": ["text"],
            "color": "#36a64f",
            "pretext": "Optional pre-text that appears above the attachment block",
            "author_name": "author_name",
            "author_link": "http://flickr.com/bobby/",
            "author_icon": "https://placeimg.com/16/16/people",
            "title": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce in ex vel magna varius viverra."
                     " Nulla sed neque hendrerit, dapibus tellus quis, vehicula sem. Ut auctor lacus aliquet ex "
                     "consequat eleifend",
            "title_link": "https://api.slack.com/",
            "text": "Optional `text` that appears within the attachment",
            "fields": [
                {
                    "title": "A field's title",
                    "value": "This field's value",
                    "short": True
                },
                {
                    "title": "A short field's title",
                    "value": "A short field's value",
                    "short": True
                },
                {
                    "title": "A second short field's title",
                    "value": "A second short field's value",
                    "short": True
                }
            ],
            "thumb_url": "http://placekitten.com/g/200/200",
            "footer": "footer",
            "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
            "ts": 123456789
        }
    ]
}

    # Size of the slack data
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json",
               'Content-Length': byte_length}

    # Posting requests after dumping the slack data
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)

    # Post request is valid or not!
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
