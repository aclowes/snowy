import importlib

from snowy import data, model, parser

frame = data.get_data()
stations = data.get_stations()
x, y = data.format_data(frame)
# x = x.resample('W-MON').mean()
x2 = x[(x.index.month == 12) | (x.index.month <= 3)]
# y2 = y.apply(lambda x: 1 if x > 0.1 else 0)
# y2.describe()

# adjust to weekly, center on zero, only winter months
snow = parser.parse_snotel('data/snotel_snowbird.csv')
# y3 = snow.prec.resample('W-MON').mean()
y2 = snow.prec
y2 = (y2 - y2.mean()) / (y2.max() - y2.min())
y2 = y2[(y2.index.month == 12) | (y2.index.month <= 3)]
y2 = y2.loc['1990-03-02':'2017-03-31']


importlib.reload(model); h = model.train_model(x2, y2)

# save image to a file
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot([1,2,3])
# fig.savefig('test.png')
