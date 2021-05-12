import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table
import numpy as np

df = pd.DataFrame(np.random.rand(6,4))
ax = plt.subplot(111, frame_on=False) # no visible frame
ax.xaxis.set_visible(False)  # hide the x axis
ax.yaxis.set_visible(False)  # hide the y axis

table(ax, df)  # where df is your data frame

plt.savefig('mytable.png')