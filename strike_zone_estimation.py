import streamlit as st

import numpy as np
import pandas as pd
from pybaseball import statcast
from plotnine import *
from dfply import *
import math

st.write('# MLBにおけるストライクゾーンの推定＆可視化')

st.write('## データ取得')

# Statcast pitch-by-pitch data on all regular season games in 2019
mlb2019 = statcast(start_dt = '2019-03-28', end_dt = '2019-09-29')

# 欠損値落としとく
mlb = \
    mlb2019 >> \
    filter_by(X.plate_x.notnull()) >> \
    filter_by(X.plate_z.notnull()) >> \
    filter_by(X.sz_top.notnull()) >> \
    filter_by(X.sz_bot.notnull())

# 概観
st.write(mlb.head())

