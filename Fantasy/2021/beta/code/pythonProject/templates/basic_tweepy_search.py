__author__ = 'chance'
import sys

sys.path.append('../modules')
import sqldb
import push
import datetime

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

end_dt = datetime.date.today()
end_dt= end_dt - datetime.timedelta(days=-2)
start_dt= end_dt - datetime.timedelta(days=3)
print(str(end_dt),str(start_dt))

q_str = "bulk opener"
print(q_str)
tweets_list = api.search(q_str, count=20, lang='en', result_type='recent')

for tweet in tweets_list:
    print("--------------")
    print(tweet.user.screen_name)
    print(tweet.created_at)
    print(tweet._json['text'])
    print("")