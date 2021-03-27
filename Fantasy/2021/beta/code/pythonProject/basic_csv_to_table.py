import numpy as np
import pandas as pd

import sys

sys.path.append('./modules')
import sqldb

# My python class: sqldb.py

bdb = sqldb.DB('Baseball.db')

csvfile = "C:\\Users\\chery\\Documents\\BBD\\BREF\\Batting\\2019spring_training.csv"
table_name = "SpringTrainingBatting"

df = pd.read_csv(csvfile)
df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
