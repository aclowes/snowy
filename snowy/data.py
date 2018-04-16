"""
Prepare the weather data
"""
import io
import os

import pandas

from . import parser

station_data = """\
724940 23234 SAN FRANCISCO INTERNATIONAL A US   CA KSFO  +37.620 -122.365 +0002.4 19730101 20171125
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
        return pandas.read_csv(cache_file, index_col=0, header=[0, 1], parse_dates=True)

    stations = get_stations()
    year_frames = []
    for year in range(1990, 2018):
        station_frames = []
        for station in stations.itertuples():
            url = 'ftp://ftp.ncdc.noaa.gov/pub/data/gsod/{year}/{station}-{wban}-{year}' \
                  '.op.gz'.format(year=year, station=station.Index, wban=station.wban)
            frame = parser.load(url, station.call_sign)
            station_frames.append(frame)

        frame = pandas.concat(station_frames, axis=1)
        year_frames.append(frame)

    frame = pandas.concat(year_frames)
    frame.to_csv(cache_file)

    # show the results
    # frame.describe().loc[:, (slice(None), 'max_temp')]

    return frame


def format_data(frame):
    stations = get_stations()

    # regularize to float 0-1
    for station in stations.itertuples():
        for column in ('temperature', 'pressure', 'precipitation', 'wind_speed'):
            values = frame.loc[:, (station.call_sign, column)]
            frame.loc[:, (station.call_sign, column + '_norm')] = \
                (values - values.mean()) / (values.max() - values.min())

    # fill missing data
    frame.fillna(0, inplace=True)

    # dependent variable is SLC precipitation
    y = frame.iloc[60:, :].loc[:, ('KSLC', 'precipitation_norm')]

    cache_file = 'data/data_x.csv'
    if os.path.exists(cache_file):
        x = pandas.read_csv(cache_file, index_col=[0], parse_dates=True)
        return x, y

    # independent variables are precipitation, temperature, pressure, and wind_speed
    # 4 variables * 6 stations * 30 days = 720 variables?
    x = []

    for index in range(len(y)):
        start = frame.index[index]
        stop = frame.index[index + 29]
        date = y.index[index]
        print(f'Now populating {date}')

        row = []
        for station in stations.itertuples():
            window = frame.loc[start:stop, station.call_sign]

            for column in ('temperature', 'pressure', 'precipitation', 'wind_speed'):
                names = [f'{station.call_sign}_{column[:4]}_{x}' for x in range(30)]
                array = [list(window[column + '_norm'])]
                array = pandas.DataFrame(array, index=[date], columns=names)
                row.append(array)

        x.append(pandas.concat(row, axis=1))

    x = pandas.concat(x)  # type: pandas.DataFrame
    x.to_csv(cache_file)

    return x, y


def group_weeks(frame):
    cache_file = 'data/data_weekly.csv'
    if os.path.exists(cache_file):
        return pandas.read_csv(cache_file, index_col=[0], parse_dates=True)

    variables = ('temperature', 'pressure', 'precipitation', 'wind_speed')
    stations = frame.columns.levels[0]
    rows = []
    week = 0

    while week < len(frame) / 7 - 9:
        columns = []
        values = []
        index = []

        for station in stations:
            if station == 'KSLC':
                start = (week + 8) * 7
                end = start + 7
                index.append(frame.index[start])
                columns.append('KSLC_prec')
                values.append(
                    frame.KSLC.precipitation_norm.iloc[start:end].mean()
                )
                continue
            for column in variables:
                series = frame[station][f'{column}_norm']
                for x in range(4):
                    start = (week + x) * 7
                    end = start + 7
                    columns.append(f'{station}_{column[:4]}_{x}')
                    values.append(series.iloc[start:end].mean())

        rows.append(
            pandas.DataFrame([values], index=index, columns=columns)
        )
        week += 1

    weekly = pandas.concat(rows)
    weekly.to_csv(cache_file)
    return weekly.drop('KSLC_prec', axis=1), weekly.KSLC_prec
