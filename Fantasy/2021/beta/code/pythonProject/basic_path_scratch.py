import pandas as pd
import numpy as np
import dataframe_image as dfi
import sys

sys.path.append('./modules')
import sqldb
import push
import fantasy
import time
import csv
from os import path
import random
from datetime import date, datetime
from datetime import timedelta
import tools
import os
from pathlib import Path

plat = tools.get_platform()
print(plat)

p = Path.cwd()
data_dir = p / 'data'
data_dir.mkdir(mode=0o755,exist_ok=True)
