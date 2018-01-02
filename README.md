# Snowman

## Will it snow?

Snowman is a weather prediction tool.

[Daily data](ftp://ftp.ncdc.noaa.gov/pub/data/gsod/readme.txt)

[Station names](ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt)

[Snotel historic data](https://wcc.sc.egov.usda.gov/nwcc/tabget?state=UT)

Make a 'framework' virtualenv to support matplotlib:

    CFLAGS="-I$(brew --prefix openssl)/include" \
    LDFLAGS="-L$(brew --prefix openssl)/lib" \
    PYTHON_CONFIGURE_OPTS="--enable-framework" \
    pyenv install 3.6.3

    PYTHON_CONFIGURE_OPTS="--enable-framework" \
    pyenv virtualenv 3.6.3 snowy

