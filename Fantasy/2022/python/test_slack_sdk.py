import sys
import re
import sys
import time

sys.path.append('./modules')
import fantasy

mode = "PROD"
fantasy = fantasy.Fantasy(mode)

from slack_sdk import WebClient

slack_api_token = os.environ["SLACK_BOT_TOKEN"]
slack_channel = os.environ["SLACK_CHANNEL"]  # "C051T1FKZUN"
slack_client = WebClient(token=slack_api_token)


def slack_process_text(text_):
    if text_ == "Adds":
        print("Tweet add drops")
        fantasy.tweet_add_drops()
    elif text_ == "Injuries":
        print("Tweet injuries")
        fantasy.run_injury_updates()
    elif re.search("^S: ", text_):
        name = text_.split(' ',1)[1]
        print(f"Stats name: {name}")
        query = f"SELECT player_name,substr(game_date,0,5)yr,stand,(p_throws)Vs,count(*)PA," \
                f"round(avg(points),4)Pts,round(avg(woba_value),4)wOBA,round(avg(xWOBA),4)xWOBA," \
                f"round(avg(isK),4)KPct,sum(isHR)HR,sum(is2b)DB,sum(isgidp)GDP " \
                f"FROM StatcastBattingEvents WHERE game_date >= '2022-04-07' and " \
                f"name like '%{name}%' group by batter, substr(game_date,0,5),p_throws " \
                f"order by substr(game_date,0,5),stand,vs,avg(points) desc LIMIT 50"
        print(query)
        fantasy.run_query(query, text_)
    else:
        query = f"Select * from ESPNRosters where Player like '%{text_}%'"
        print(query)
        fantasy.run_query(query, text_)


def read_slack():
    slack_most_recent = ""
    slack_first_run = True
    while True:
        history = slack_client.conversations_history(channel=slack_channel, tokem=slack_api_token, limit=1)
        msgs = history['messages']
        if len(msgs) > 0:
            for msg in msgs:
                text = msg['text']
                if text != slack_most_recent:
                    try:
                        slack_most_recent = text
                        if not slack_first_run:
                            slack_process_text(text)
                        else:
                            print(F"Skipping first run")
                            slack_first_run = False
                    except Exception as ex:
                        fantasy.push_instance.push(f"Error in push_instance, Error: {str(ex)}")
                else:
                    print(f"Skipping most recent post: {text}")
        time.sleep(5)


def main():
    read_slack()


if __name__ == "__main__":
    main()
