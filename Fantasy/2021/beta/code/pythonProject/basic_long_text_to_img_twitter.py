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

text = "Lorem ipsum dolor sit amet,\n" \
       " consectetuer adipiscing elit. \n" \
       "Aenean commodo ligula eget dolor. \n" \
       "Aenean massa. Cum sociis natoque\n" \
       " penatibus et magnis dis parturient\n" \
       " montes, nascetur ridiculus mus.\n" \
       " Donec quam felis, ultricies nec,\n" \
       " pellentesque eu, pretium quis, sem.\n" \
       " Nulla consequat massa quis enim.\n" \
       " Donec pede justo, fringilla vel,\n" \
       " aliquet nec, vulputate eget, arcu.\n" \
       " In enim justo, rhoncus ut, imperdiet a,\n" \
       " venenatis vitae, justo. Nullam dictum\n" \
       " felis eu pede mollis pretium. \n" \
       "Integer tincidunt. Cras dapibus. \n" \
		"Integer tincidunt. Cras dapibus. \n" \
		"Integer tincidunt. Cras dapibus. \n" \
       "Vivamus elementum semper nisi. \n" \
       "Aenean vulputate eleifend tellus.\n " \
       "Aenean leo ligula, porttitor eu,\n"

text_list = text.split("\n")
inst.push_list_twtr(text_list)


# df_styled = df.style.background_gradient()  # adding a gradient based on values in cell





