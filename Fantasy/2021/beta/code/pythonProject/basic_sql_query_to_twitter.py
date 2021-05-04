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

inst = push.Push()
lol = []
index = list()
name = "Corey Seager"
query = "select * from ESPNRosters where Player like '%" + name + " %'"
col_headers, rows = bdb.select_w_cols(query)

for row in rows:
	#strrow = inst.string_from_list(row)
	lol.append(row)
	index.append("")
bdb.close()

df = pd.DataFrame(lol, columns=col_headers, index=index)

# df_styled = df.style.background_gradient()  # adding a gradient based on values in cell

img = "mytable.png"
dfi.export(df, img)

mode = "PROD"

#inst.push_list(lol)
inst.tweet_media(img, query)
