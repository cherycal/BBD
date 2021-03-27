import sys

sys.path.append('./modules')
import push
import pandas as pd
import fantasy
import dataframe_image as dfi
from datetime import datetime

mode = "PROD"
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()
ts = datetime.now()  # current date and time
formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
# All in push.py
# APP ID: 20456708

# APIKEY = "xFROaRKqUGekYP7XtybD5SKic"
# APISECRETKEY = "9qQGFm27JDOCJtMs3SnlBPRhOeAv28ujqy6qXoUbB8t8q1zeQr"
# ACCESSTOKEN = "1375606437410299905-47aXO2g5nwt5K0p1Qw69iVKJ5Mz4wN"
# ACCESSTOKENSECRET = "pF84t0Xukgaaf4QL6khVTuBjsLBMdfH0ibuJSGa0CdUnr"

# BEARER TOKEN: AAAAAAAAAAAAAAAAAAAAAAQlOAEAAAAAuDfNbFusmC3ug5pq2kpvI5zpmbg%3DViQCxXGUBXHJ6sZZY5SSPA3VkqGkOUJf7BsYbm5WndF0jUgbU1

# Authenticate to Twitter
# auth = tweepy.OAuthHandler(APIKEY, APISECRETKEY)
# auth.set_access_token(ACCESSTOKEN, ACCESSTOKENSECRET)
#
# # Create API object
# api = tweepy.API(auth)
#
# # Create a tweet
# api.update_status("Hello Tweepy")

lol = []
index = list()
col_headers, rows = bdb.select_w_cols("select FirstName || \" \" || LastName as Name, IP, SO, BB, ERA, WHIP, HR"
                                      " from SpringTrainingPitching where Year = 2021 and IP > 13 and SO > IP * 1.2 order by SO desc")

for row in rows:
	lol.append(row)
	index.append("")
bdb.close()

df = pd.DataFrame(lol, columns=col_headers, index=index)

# df_styled = df.style.background_gradient()  # adding a gradient based on values in cell

img = "mytable.png"
dfi.export(df, img)

mode = "PROD"

inst = push.Push()
inst.tweet_media(img, "Spring Training 2021 SO > 15 and SO > IP * 1.2")
