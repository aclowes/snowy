"""
Prepare the weather data
"""
import io

import os
import urllib.error

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


def get_data():
    cache_file = 'data.csv'
    if os.path.exists(cache_file):
        frame = pandas.read_csv(cache_file, index_col=[0, 1])
        return frame

    stations = get_stations()
    frames = []
    for station in stations.itertuples():
        for year in range(1990, 2018):
            filename = 'ftp://ftp.ncdc.noaa.gov/pub/data/gsod/{year}/{station}-{wban}-{year}' \
                       '.op.gz'.format(year=year, station=station.Index, wban=station.wban)
            frame = parser.parse(filename)
            frames.append(frame)

    frame = pandas.concat(frames)

    frame.to_csv(cache_file)


def split():
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(
        X, y, test_size=0.2, random_state=42
    )
