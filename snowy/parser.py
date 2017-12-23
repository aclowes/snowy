"""
Parser for GSOD weather data format

ftp://ftp.ncdc.noaa.gov/pub/data/gsod/readme.txt
"""
import os
import time
import urllib.error
import urllib.request

import pandas

columns = (
    # start, stop, name, missing, type
    (0, 6, 'station', None),
    (7, 12, 'wban', None),
    (14, 22, 'date', None),
    (24, 30, 'temperature', '9999.9'),
    (31, 33, 'temp_count', None),
    (35, 41, 'dew_point', '9999.9'),
    (42, 44, 'dew_count', None),
    (46, 52, 'sea_level', '9999.9'),
    (53, 55, 'sea_level_count', None),
    (57, 63, 'pressure', '9999.9'),
    (64, 66, 'pressure_count', None),
    (68, 73, 'visibility', '999.9'),
    (74, 76, 'visibility_count', None),
    (78, 83, 'wind_speed', '999.9'),
    (84, 86, 'wind_speed_count', None),
    (88, 93, 'max_speed', '999.9'),
    (95, 100, 'gust_speed', '999.9'),
    (102, 108, 'max_temp', '9999.9'),
    (108, 109, 'max_flag', None),
    (110, 116, 'min_temp', '9999.9'),
    (118, 123, 'precipitation', '99.99'),
    (123, 124, 'precipitation_flag', None),
    (125, 130, 'snow_depth', '999.9'),
    (132, 133, 'fog', None),
    (132, 133, 'rain', None),
    (132, 133, 'snow', None),
    (132, 133, 'hail', None),
    (132, 133, 'thunder', None),
    (132, 133, 'tornado', None),
)


def load(url, call_sign):
    filename = os.path.join('data', url.split('/')[-1])
    if not os.path.exists(filename):

        while True:
            try:
                time.sleep(5)
                print('Fetching {}'.format(url))
                with urllib.request.urlopen(url) as request:
                    with open(filename, 'wb') as file:
                        file.write(request.read())
                break
            except urllib.error.URLError as exc:
                print('Could not load {} exception {}'.format(url, exc))
                time.sleep(10)

    return parse(filename, call_sign)


def parse(filename, call_sign):
    start, stop, names, missing = zip(*columns)
    missing = dict(zip(names, missing))
    positions = list(zip(start, stop))
    frame = pandas.read_fwf(filename, colspecs=positions, names=names, na_values=missing,
                            skiprows=1, compression='gzip', index_col=2)
    # convert the index to datetime and add station to the columns
    frame.index = pandas.DatetimeIndex(pandas.to_datetime(frame.index, format='%Y%m%d'))
    frame.columns = pandas.MultiIndex.from_product(([call_sign], frame.columns))
    return frame
