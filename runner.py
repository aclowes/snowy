import os
import importlib

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas

from snowy import data, model, parser

frame = data.get_data()
stations = data.get_stations()
x, y = data.format_data(frame)
snow = parser.parse_snotel('data/snotel_snowbird.csv')

y3 = snow.prec.loc[y.index[0]:y.index[-1]]
y3 = y3.resample('W-MON').mean()
y3 = (y3 - y3.mean())/(y3.max() - y3.min())
y3 = y3[(y3.index.month == 12) | (y3.index.month <= 3)]

# y2 = y.apply(lambda x: 1 if x > 0.1 else 0)
# y2.describe()

x2 = x[(x.index.month == 12) | (x.index.month <= 3)]
y2 = y[(y.index.month == 12) | (y.index.month <= 3)]

importlib.reload(model); h = model.train_model(x2, y3)
