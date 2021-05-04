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

inst = push.Push()
lol = []
index = list()

name = "Houser"

query = "select * from ESPNRosters where Player like '%" + name + "%'"
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
