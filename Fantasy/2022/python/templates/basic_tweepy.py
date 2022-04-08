__author__ = 'chance'
import sys
import time

import pandas as pd

sys.path.append('../modules')
import sqldb
import push
from datetime import datetime

# My python class: sqldb.py
push_instance = push.Push(wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')
# DB location: ('C:\\Ubuntu\\Shared\\data\\Baseball.db')

def extract_timeline_as_df(user_timeline):
    columns = set()
    allowed_types = [str, int]
    tweets_data = []
    for status in user_timeline:
        status_dict = dict(vars(status))
        keys = status_dict.keys()
        single_tweet_data = {"user": status.user.screen_name, "author": status.author.screen_name}
        for k in keys:
            try:
                v_type = type(status_dict[k])
            except:
                v_type = None
            if v_type != None:
                if v_type in allowed_types:
                    single_tweet_data[k] = status_dict[k]
                    columns.add(k)
        tweets_data.append(single_tweet_data)


    header_cols = list(columns)
    header_cols.append("user")
    header_cols.append('author')
    df = pd.DataFrame(tweets_data, columns=header_cols)
    return df


api = push_instance.get_twitter_api()
auth = push_instance.get_twitter_auth()
auth_url = auth.get_authorization_url()

tweet_cache = list()

users = ["bleachernation","gsmlbpicks"]

print(api.saved_searches())

exit(0)

while(True):
    print(f'{datetime.now().strftime("%Y%m%d-%H%M%S")}')
    #print(api.rate_limit_status())
    for u in users:
        user = api.get_user(u)
        user_timeline = user.timeline(count = 4)
        #my_timeline = api.home_timeline()

        df2 = extract_timeline_as_df(user_timeline)

        tweet_dict = df2[['id','text']].to_dict('index')

        for key in tweet_dict.keys():
            id = tweet_dict[key]['id']
            text = tweet_dict[key]['text']
            if id not in tweet_cache:
                tweet_cache.append(id)
                print(user.screen_name, text)
                #push_instance.push(id, text)
                time.sleep(5)

        time.sleep(5)

    time.sleep(20)





#print(api.me().screen_name)