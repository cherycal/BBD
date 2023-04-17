import sys

sys.path.append('../modules')
import pandas as pd
import fantasy
import dataframe_image as dfi
from datetime import datetime
import os

cwd = os.getcwd()
print(cwd)

mode = "PROD"
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()
ts = datetime.now()  # current date and time
formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")

lol = []
index = list()
col_headers, rows = bdb.select_w_cols("select UpdateTime,PlayerName,TeamName,LegType,LeagueID "
                             "from AddDrops where UpdateDate = 20210326 "
                             "order by UpdateTime desc")

for row in rows:
	lol.append(row)
	index.append("")
bdb.close()

df = pd.DataFrame(lol, columns=col_headers, index=index)

# df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
print(df)
img = "./mytable.png"
dfi.export(df, img,table_conversion="matplotlib")

mode = "PROD"

inst = push.Push()
inst.tweet_media(img, "Table created at " + str(formatted_date_time))
