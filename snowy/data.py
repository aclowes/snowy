"""
Prepare the weather data
"""
import io
import os
import time
import datetime

import pandas
import sklearn

from . import parser

station_data = """\
724940 23234 SAN FRANCISCO INTERNATIONAL A US   CA KSFO  +37.620 -122.365 +0002.4 19730101 20171125
719170 99999 EUREKA                        CA      CWEU  +79.983 -085.933 +0010.0 19470501 20171124
727930 24233 SEATTLE-TACOMA INTERNATIONAL  US   WA KSEA  +47.444 -122.314 +0112.8 19480101 20171125
724880 23185 RENO/TAHOE INTERNATIONAL AIRP US   NV KRNO  +39.484 -119.771 +1344.2 19430105 20171125
723677 23054 LAS VEGAS MUNICIPAL ARPT      US   NM KLVS  +35.654 -105.142 +2095.2 19460801 20171125
722950 23174 LOS ANGELES INTERNATIONAL AIR US   CA KLAX  +33.938 -118.389 +0029.6 19440101 20171125
725720 24127 SALT LAKE CITY INTERNATIONAL  US   UT KSLC  +40.778 -111.969 +1287.8 19411101 20171125
"""
columns = (
    (0, 6, 'station'),
    (7, 12, 'wban'),
    (13, 42, 'name'),
    (43, 45, 'country'),
    (48, 50, 'state'),
    (51, 56, 'call_sign'),
    (57, 64, 'latitude'),
    (65, 73, 'longitude'),
    (74, 81, 'altitude'),
    (82, 90, 'first_date'),
    (91, 99, 'last_date'),
)


def get_stations():
    start, stop, names = zip(*columns)
    positions = list(zip(start, stop))
    return pandas.read_fwf(
        io.StringIO(station_data), colspecs=positions, names=names,
        parse_dates=[9, 10], index_col=[0]
    )


def get_station_history():
    start, stop, names = zip(*columns)
    positions = list(zip(start, stop))
    return pandas.read_fwf(
        'isd-history.txt', colspecs=positions, names=names,
        parse_dates=[9, 10], index_col=[0], skiprows=21, skip_blank_lines=True
    )
    # history[(history.first_date < datetime.datetime(1974, 1, 1)) & (history.last_date > datetime.datetime(2017, 11, 1))
    # & (history.state == 'UT') & (history.altitude > 2000)]


def get_data():
    cache_file = 'data/data.csv'
    if os.path.exists(cache_file):
        return pandas.read_csv(cache_file, index_col=[0, 1])

    stations = get_stations()
    frames = []
    for station in stations.itertuples():
        for year in range(1990, 2018):
            filename = 'ftp://ftp.ncdc.noaa.gov/pub/data/gsod/{year}/{station}-{wban}-{year}' \
                       '.op.gz'.format(year=year, station=station.Index, wban=station.wban)
            frame = parser.load(filename)
            frames.append(frame)

    frame = pandas.concat(frames)
    frame.to_csv(cache_file)

    return frame


def format_data(frame):
    # regularize to float 0-1
    for column in ('temperature', 'pressure', 'precipitation', 'wind_speed'):
        values = frame[column]
        frame.loc[:, column + '_norm'] = (values - values.mean()) / (values.max() - values.min())

    # dependent variable is SLC precipitation
    y = frame.loc[725720]['precipitation_norm'][60:2000]

    cache_file = 'data/data_x.csv'
    if os.path.exists(cache_file):
        x = pandas.read_csv(cache_file, index_col=[0])
        return x, y

    # independent variables are precipitation, temperature, pressure, and wind_speed
    # 4 variables * 6 stations * 30 days = 720 variables?
    stations = get_stations()
    x = []

    for index in range(len(y)):
        date = y.index[index]
        print('Now indexing {}'.format(date))

        row = []
        for station in stations.itertuples():
            window = frame.loc[station.Index][index:index + 30]

            for column in ('temperature', 'pressure', 'precipitation', 'wind_speed'):
                columns = ['{}_{}_{}'.format(station.call_sign, column, x) for x in range(30)]
                array = [list(window[column + '_norm'])]
                array = pandas.DataFrame(array, index=[date], columns=columns)
                row.append(array)

        x.append(pandas.concat(row, axis=1))

    x = pandas.concat(x)
    x.to_csv(cache_file)

    return x, y
