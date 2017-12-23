import os
import importlib

import pandas

from snowy import data, model, parser

frame = data.get_data()
stations = data.get_stations()
x, y = data.format_data(frame)

m = model.train_model(x, y)

# TODO graph pred vs y_test and see if its generally right
