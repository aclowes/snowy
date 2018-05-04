"""
Parser for GSOD weather data format

ftp://ftp.ncdc.noaa.gov/pub/data/gsod/readme.txt
"""
import datetime
import io
import time
import urllib.error
import urllib.request

import pandas

from google.cloud import storage

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


def load(year, station):
    """
    Get the weather history for the given year and station record
    either from cache or the FTP.
    """

    url = 'ftp://ftp.ncdc.noaa.gov/pub/data/gsod/{year}/{station}-{wban}-{year}' \
          '.op.gz'.format(year=year, station=station.Index, wban=station.wban)

    client = storage.Client()
    bucket = client.bucket('static.yawn.live')
    filename = url.split('/')[-1]
    blob = bucket.blob(f'snowy/data/{filename}')

    if year >= (datetime.date.today() - datetime.timedelta(days=7)).year and blob.exists():
        # get a new copy with the latest data
        blob.delete()

    if not blob.exists():
        while True:
            try:
                time.sleep(5)  # avoid throttling
                print('Fetching {}'.format(url))
                request = urllib.request.urlopen(url)
                contents = request.read()
                blob.upload_from_string(contents)
                break
            except urllib.error.URLError as exc:
                print('Could not load {} exception {}'.format(url, exc))
                time.sleep(5)
    else:
        contents = blob.download_as_string()

    return contents


def parse(contents, call_sign):
    """Parse the historical weather file format"""
    start, stop, names, missing = zip(*columns)
    missing = dict(zip(names, missing))
    positions = list(zip(start, stop))
    frame = pandas.read_fwf(io.StringIO(contents), colspecs=positions, names=names, na_values=missing,
                            skiprows=1, compression='gzip', index_col=2)
    # convert the index to datetime and add station to the columns
    frame.index = pandas.DatetimeIndex(pandas.to_datetime(frame.index, format='%Y%m%d'))
    frame.columns = pandas.MultiIndex.from_product(([call_sign], frame.columns))
    return frame


def parse_snotel(filename):
    frame = pandas.read_csv(
        filename, index_col=[0], parse_dates=True, skiprows=58,
    )
    frame.columns = ['water', 'total_prec', 'max', 'min', 'avg', 'prec']
    return frame[:-1]
