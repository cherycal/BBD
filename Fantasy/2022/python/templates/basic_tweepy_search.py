__author__ = 'chance'

import sys
import time

sys.path.append('../modules')
import sqldb
import push
from datetime import datetime
import fantasy
import os

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

q_strs = {"alerts baseball name": "fantasy.run_query()"}


# time_str = "2022-04-11 05:19:08"
# then = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
# now = datetime.utcnow()
# diff = now - then
# print(diff.seconds)
# exit(0)
sleepint = 15
while 1:

    for q_str in q_strs.keys():

        tweets_list = api.search(q_str, count=20, lang='en', result_type='recent')

        for tweet in tweets_list:
            id = tweet._json['id']
            text = tweet._json['text']
            term = str(text)
            term = term.replace("alerts baseball name ","")
            print(f'search term: {term}')
            if id not in tweet_cache:
                print("--------------")
                print(tweet.user.screen_name)
                print("--------------")
                print(tweet.created_at)
                #age = datetime.strptime(tweet.created_at, "%Y-%m-%d %H:%M:%S")
                now = datetime.utcnow()
                diff = now - tweet.created_at
                print(f'{diff.seconds} seconds ago')
                print("--------------")
                print(id)
                print("--------------")
                print(tweet._json['user']['name'])
                print("--------------")
                print(tweet._json['text'])
                print("--------------")
                print(f'Function: {q_str} => {q_strs[q_str]}')
                tweet_cache.append(tweet._json['id'])
                if diff.seconds < sleepint * 2:
                    query = f'SELECT Player, Team, LeagueID, Position FROM ESPNRosters WHERE Player like "%{term}%" order by Player, LeagueId'
                    print(f'query: {query}')
                    fantasy.run_query(query)
                    # q_strs[q_str]
                else:
                    print(f'Not processing tweet because it is too old ({diff.seconds} seconds)')
            else:
                print(f'ID: {id} already processed')

    print(f'Sleeping for {sleepint} seconds at {datetime.now()}')
    time.sleep(sleepint)
