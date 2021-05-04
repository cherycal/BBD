import numpy as np
import pandas as pd

import sys

sys.path.append('./modules')
import sqldb

# My python class: sqldb.py

bdb = sqldb.DB('Baseball.db')

bdb.cmd("ALTER TABLE IDMapAdjustments ADD COLUMN notes2 text")

#update BRefProjectionBatting set PTS = R+RBI+SB+BB-SO+"1B"+2*"2B"+3*"3B"+4*HR
