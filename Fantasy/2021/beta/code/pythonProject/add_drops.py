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
formatted_date_time = ts.strftime("%Y%m%d-%I%M%S.f")
date8 = formatted_date_time = ts.strftime("%Y%m%d")


inst = push.Push()
lol = []
index = list()
query = "select UpdateDate, PlayerName, TeamName, LegType from AddDrops where UpdateDate = " + date8
print("Query: " + query)
col_headers, rows = bdb.select_w_cols(query)

for row in rows:
	lol.append(row)
	index.append("")
bdb.close()

df = pd.DataFrame(lol, columns=col_headers, index=index)

# df_styled = df.style.background_gradient()  # adding a gradient based on values in cell

img = "mytable.png"
dfi.export(df, img)

mode = "PROD"

inst.tweet_media(img, query)
