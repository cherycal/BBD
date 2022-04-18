__author__ = 'chance'

import sys
import time

sys.path.append('./modules')
import sqldb
import push
from datetime import datetime
import fantasy
import os
import espn_h2h_current_scores

mode = "PROD"
fantasy = fantasy.Fantasy(mode, caller=os.path.basename(__file__))

# My python class: sqldb.py
push_instance = push.Push(wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')
# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')

api = push_instance.get_twitter_api()
auth = push_instance.get_twitter_auth()
auth_url = auth.get_authorization_url()

tweet_cache = list()


# end_dt = datetime.date.today()
# end_dt = end_dt - datetime.timedelta(days=-2)
# start_dt = end_dt - datetime.timedelta(days=3)
# print(str(end_dt), str(start_dt))



# q_strs = {"alerts baseball schedule": fantasy.tweet_daily_schedule,
#           "alerts baseball adds": fantasy.tweet_add_drops,
#           "alerts baseball flip score": espn_head_to_head_scores.get_page}

q_strs = {"alerts baseball flip score": espn_h2h_current_scores.get_page}

sleepint = 8
tweetage = 50

while 1:

    for q_str in q_strs.keys():

        print(f'Searching term {q_str}')
        tweets_list = api.search(q_str, count=20, lang='en', result_type='recent')

        for tweet in tweets_list:
            tid = tweet._json['id']
            text = tweet._json['text']
            term = str(text)
            term = term.replace("alerts baseball name ", "")

            if tid not in tweet_cache:
                print(tweet._json['text'])
                tweet_cache.append(tid)
                now = datetime.utcnow()
                diff = now - tweet.created_at
                now = datetime.utcnow()
                print(f'{diff.seconds} seconds ago')
                if diff.seconds < tweetage:
                    print("--------------")
                    print(tweet.user.screen_name)
                    print(tweet.created_at)
                    # age = datetime.strptime(tweet.created_at, "%Y-%m-%d %H:%M:%S")
                    now = datetime.utcnow()
                    diff = now - tweet.created_at
                    print(f'{diff.seconds} seconds ago')
                    print(tid)
                    print(tweet._json['user']['name'])
                    print("--------------")
                    print(tweet._json['text'])
                    print("--------------")
                    print(f'Function: {q_str} => {q_strs[q_str]}')
                    # query = f'SELECT Player, Team, LeagueID, Position FROM ESPNRosters WHERE Player like "%{term}%" order by Player, LeagueId'
                    # print(f'query: {query}')
                    # fantasy.run_query(query)
                    q_strs[q_str]()
                else:
                    pass
                    # print(f'Not processing tweet because it is too old ({diff.seconds} seconds)')
            else:
                pass
                # print(f'ID: {id} already processed')


        print(f'Sleeping for {sleepint} seconds at {datetime.now()}')
        time.sleep(sleepint)
