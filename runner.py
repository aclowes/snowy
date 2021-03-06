import importlib
import os
import sys

from snowy import data, model, parser

fresh = True


def runner():
    frame = data.get_data(fresh)
    x, y = data.format_data(frame, fresh)
    x2 = x[(x.index.month == 12) | (x.index.month <= 3)]

    # adjust to weekly, center on zero, only winter months
    snow = parser.parse_snotel('data/snotel_snowbird.csv')
    y2 = snow.prec
    y2 = (y2 - y2.mean()) / (y2.max() - y2.min())
    y2 = y2[(y2.index.month == 12) | (y2.index.month <= 3)]
    # cut to period covered by weather data
    y2 = y2.loc[x2.index[0]:x2.index[-1]]

    h = model.train_model(x2, y2)

# NOTES: resample to weekly data, cut off values
# x = x.resample('W-MON').mean()
# y3 = snow.prec.resample('W-MON').mean()
# y2 = y.apply(lambda x: 1 if x > 0.1 else 0)
# y2.describe()


def local_runner():
    global fresh
    fresh = False
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'data/YAWN-service-account.json'
    runner()
    # importlib.reload(model); h = model.train_model(x2, y2)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        local_runner()
    else:
        runner()
