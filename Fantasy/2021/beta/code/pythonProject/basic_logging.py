__author__ = 'chance'

import dataframe_image
import dataframe_image as dfi
import numpy as np
import pandas as pd


df = pd.DataFrame(np.random.rand(6,4))
df_styled = df.style.background_gradient()
df_styled.export_png('df_styled.png')

df.dfi.export('image2.png')

