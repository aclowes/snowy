"""
Download and format the weather data
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
    """Parse the list of stations to download"""
    start, stop, names = zip(*columns)
    positions = list(zip(start, stop))
    return pandas.read_fwf(
        io.StringIO(station_data), colspecs=positions, names=names,
        parse_dates=[9, 10], index_col=[0]
    )


def get_station_history():
    """
    Returns what weather stations are available for download

    We actually download just the stations listed above in `station_data`. This
    might be useful to search for stations like this:

    history[(history.first_date < datetime.datetime(1974, 1, 1))
            & (history.last_date > datetime.datetime(2017, 11, 1))
            & (history.state == 'UT') & (history.altitude > 2000)]
    """
    start, stop, names = zip(*columns)
    positions = list(zip(start, stop))
    return pandas.read_fwf(
        'isd-history.txt', colspecs=positions, names=names,
        parse_dates=[9, 10], index_col=[0], skiprows=21, skip_blank_lines=True
    )


def get_data(fresh=True):
    """Get the weather history for all stations of interest since 1990"""

    cache_file = 'data/data.csv'
    if os.path.exists(cache_file) and not fresh:
        return pandas.read_csv(cache_file, index_col=0, header=[0, 1], parse_dates=True)

    stations = get_stations()
    year_frames = []
    for year in range(1990, 2018):
        print(f'Now fetching history for {year}')
        station_frames = []
        for station in stations.itertuples():
            raw_data = parser.load(year, station)
            frame = parser.parse(raw_data, station.call_sign)
            station_frames.append(frame)

        frame = pandas.concat(station_frames, axis=1)
        year_frames.append(frame)

    frame = pandas.concat(year_frames)  # type: pandas.DataFrame
    frame.to_csv(cache_file)
    return frame


def format_data(frame, fresh=True):
    stations = get_stations()

    # regularize to float 0-1
    for station in stations.itertuples():
        for column in ('temperature', 'pressure', 'precipitation', 'wind_speed'):
            values = frame.loc[:, (station.call_sign, column)]
            frame.loc[:, (station.call_sign, column + '_norm')] = \
                (values - values.mean()) / (values.max() - values.min())

    # fill missing data
    frame.fillna(0, inplace=True)

    # dependent variable is SLC precipitation, forecasting 60 days in the future
    y = frame.iloc[60:, :].loc[:, ('KSLC', 'precipitation_norm')]

    cache_file = 'data/data_x.csv'
    if os.path.exists(cache_file) and not fresh:
        x = pandas.read_csv(cache_file, index_col=[0], parse_dates=True)
        return x, y

    # independent variables are precipitation, temperature, pressure, and wind_speed
    # 4 variables * 6 stations * 30 days = 720 variables?
    data = {}
    for offset in range(30):
        for station in stations.itertuples():
            window = frame.iloc[offset:offset - 60].loc[:, station.call_sign]
            for column in ('temperature', 'pressure', 'precipitation', 'wind_speed'):
                data[f'{station.call_sign}_{column[:4]}_{offset}'] = window[column + '_norm'].values

    x = pandas.DataFrame(data, index=y.index)
    x.to_csv(cache_file)

    return x, y
