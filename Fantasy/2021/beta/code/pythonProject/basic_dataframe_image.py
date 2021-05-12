__author__ = 'chance'

import dataframe_image
import dataframe_image as dfi
import numpy as np
import pandas as pd
import sys
sys.path.append('./modules')
import push
inst = push.Push()


df = pd.DataFrame(np.random.rand(6,4))
df_styled = df.style.background_gradient()

img_styled = 'df_styled.png'
df_styled.export_png(img_styled, table_conversion='matplotlib')

#img = 'image2.png'
#df.dfi.export(img)

inst.tweet_media(img_styled,"Random number grid")

