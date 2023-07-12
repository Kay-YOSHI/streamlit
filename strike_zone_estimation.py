import streamlit as st

import numpy as np
import pandas as pd
from pybaseball import statcast
from plotnine import *
from dfply import *
import math

st.write("# MLBにおける投球分布の可視化")

st.write("## データ取得")

# Statcast pitch-by-pitch data on all regular season games in 2019
mlb2019 = statcast(start_dt="2019-03-28", end_dt="2019-04-30")

# 欠損値落としとく
mlb = (
    mlb2019
    >> filter_by(X.plate_x.notnull())
    >> filter_by(X.plate_z.notnull())
    >> filter_by(X.sz_top.notnull())
    >> filter_by(X.sz_bot.notnull())
    >> filter_by(X.balls.notnull())
    >> filter_by(X.strikes.notnull())
)

# 概観
st.write(mlb.shape)
st.write(mlb.head())

st.write("## 投球分布")

# 見逃しかつファストボールに絞る＆重いのでランダムサンプリングしとく
dist = (
    mlb
    >> filter_by(X.pitch_type == "FF")
    >> filter_by((X.description == "called_strike") | (X.description == "ball"))
    >> mutate(code=if_else(X.description == "called_strike", "Called Strike", "Ball"))
    >> unite("count", X.balls, X.strikes, sep="-", remove=False, na_action="maintain")
    # >> filter_by(X.count == "0-2")
    >> sample(n=10000)
)

# ルールブック上のストライクゾーン
# 上限と下限は打者平均とする．なお，ホームプレート＝17インチ，ボール＝9インチ（1インチ＝1/12フィート）．
plate_width = (17 + 2 * (9 / math.pi)) / 12
xm = [
    -(plate_width / 2),
    plate_width / 2,
    plate_width / 2,
    -(plate_width / 2),
    -(plate_width / 2),
]
zm = [
    dist["sz_bot"].mean(),
    dist["sz_bot"].mean(),
    dist["sz_top"].mean(),
    dist["sz_top"].mean(),
    dist["sz_bot"].mean(),
]
sz_mlb = pd.DataFrame({"xm": xm, "zm": zm})

# 可視化
pdist = (
    ggplot(dist, aes(x="plate_x", y="plate_z"))
    + geom_point(aes(color="code"), alpha=1.0)
    + geom_path(sz_mlb, aes(x="xm", y="zm"), linejoin="round", size=1.0)
    + coord_equal()
    + scale_x_continuous(name="Horizontal location (ft.)", limits=(-2.0, 2.0))
    + scale_y_continuous(name="Vertical location (ft.)", limits=(0.0, 5.0))
    + labs(
        title="Pitch distribution",
        subtitle="(Randomly sampled 10,000 obs.)",
        caption="*Catcher's perspective.",
    )
    + theme_bw()
)
st.pyplot(ggplot.draw(pdist))
