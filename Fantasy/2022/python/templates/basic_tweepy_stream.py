__author__ = 'chance'
import sys

sys.path.append('../modules')
import sqldb
import push

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
import tweepy
#override tweepy.StreamListener to add logic to on_status

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print("")
        print("---------------")
        print(status.user)
        print("----")
        print(status.user.screen_name)
        print("----")
        print(status.text)
        print("---------------")
        print("")
        # push_instance.push("Stream", status.text)
        # push_instance.tweet(status.text)
        # time.sleep(5)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

myStream.filter(track=['lineup MLB','odorizzi',"#MLBPicks"])
# myStream.filter(follow=['FantasyLabsMLB','@FantasyLabsMLB',
#                         'RotoWireMLB','GSMLBPicks', '@GSMLBPicks',
#                         'agholorpooch','@agholorpooch'])
