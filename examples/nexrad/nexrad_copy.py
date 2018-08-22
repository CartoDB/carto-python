import logging
from datetime import datetime, timedelta
import os
import sys
import argparse

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from carto.sql import CopySQLClient

import numpy as np
from siphon.radarserver import RadarServer
from siphon.cdmr import Dataset

# Example of CopySQLClient usage to stream data from NEXRAD Level 2
# data to CARTO.
#
# For more information see the following URL's:
#   - https://carto.com/blog/mapping-nexrad-radar-data/
#   - https://gist.github.com/stuartlynn/a7868cf8ca02931a6408
#   - http://nbviewer.jupyter.org/gist/dopplershift/356f2e14832e9b676207

# Set up a logger
logger = logging.getLogger('nexrad_copy')
logger.setLevel(logging.INFO)

# Parse input arguments
parser = argparse.ArgumentParser(description=(
    'Example of CopySQLClient usage to stream data from NEXRAD Level 2'
    ' data to CARTO.'
))

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ.get('CARTO_API_URL', ''),
                    help=('Set the base URL. For example:'
                          ' https://username.carto.com/'
                          ' (defaults to env variable CARTO_API_URL)'))

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ.get('CARTO_API_KEY', ''),
                    help=('Api key of the account'
                          ' (defaults to env variable CARTO_API_KEY)'))

args = parser.parse_args()

if not args.CARTO_BASE_URL or not args.CARTO_API_KEY:
    sys.exit(parser.print_usage())

auth_client = APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY)
sql_client = SQLClient(auth_client)
copy_client = CopySQLClient(auth_client)

# Create a table suitable to receive the data
logger.info('Creating table nexrad_copy_example...')
sql_client.send("""CREATE TABLE IF NOT EXISTS nexrad_copy_example (
  the_geom geometry(Geometry,4326),
  reflectivity numeric
)""")
sql_client.send(
    "SELECT CDB_CartodbfyTable(current_schema, 'nexrad_copy_example')")
logger.info('Done')

logger.info('Trying to connect to the THREDDS radar query service')
rs = RadarServer(
    'http://thredds.ucar.edu/thredds/radarServer/nexrad/level2/IDD/')

logger.info('Quering data from the station')
query = rs.query()
query.stations('KLVX').time(datetime.utcnow())
assert rs.validate_query(query)

catalog = rs.get_catalog(query)
logger.info('Avaliable datasets: %s' % catalog.datasets)
logger.info('Using the first one')
ds = list(catalog.datasets.values())[0]
data = Dataset(ds.access_urls['CdmRemote'])
logger.info('Got the following data: %s' % data.Title)
logger.info(data.Summary)


# A helper method to clean up the data
def raw_to_masked_float(var, data):
    # Values come back signed. If the _Unsigned attribute is set, we
    # need to convert from the range [-127, 128] to [0, 255].
    if var._Unsigned:
        data = data & 0xFF

    # Mask missing points
    data = np.ma.array(data, mask=(data == 0))

    # Convert to float using the scale and offset
    return data * var.scale_factor + var.add_offset

# We pull out the variables we need for azimuth and range, as well as
# the data itself.
logger.info('Pulling out some of the variables...')
sweep = 0
ref_var = data.variables['Reflectivity_HI']
ref_data = ref_var[sweep]
rng = data.variables['distanceR_HI'][:]
az = data.variables['azimuthR_HI'][sweep]
logger.info('ref_data.shape: {}'.format(ref_data.shape))


# Calculate a (lat, lon) pair offset by a (dist, bearing) pair
# https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing
def offset_by_meters(lat, lon, dist, bearing):
    R = 6378.1
    bearing_rads = np.deg2rad(az)[:, None]
    dist_km = dist / 1000.0

    lat1 = np.radians(lat)
    lon1 = np.radians(lon)

    lat2 = np.arcsin(np.sin(lat1) * np.cos(dist_km/R) +
                     np.cos(lat1) * np.sin(dist_km/R) * np.cos(bearing_rads))
    lon2 = lon1 + np.arctan2(np.sin(bearing_rads) * np.sin(dist_km/R)
                             * np.cos(lat1),
                             np.cos(dist_km/R) - np.sin(lat1) * np.sin(lat2))

    return np.degrees(lat2), np.degrees(lon2)

# Then convert the raw data to floating point values, and the relative
# polar coordinates to lat/lon
logger.info('Converting the data...')
ref = raw_to_masked_float(ref_var, ref_data)
lat, lon = offset_by_meters(
    data.StationLatitude, data.StationLongitude, rng, az)
logger.info('Done')


# This generator builds the rows without needing to buffer all of them
# in memory.  Alternatively a StringIO (python2) or a BytesIO
# (python3) buffer could be used.
def rows():
    for ix, iy in np.ndindex(ref.shape):
        value = ref[ix, iy]
        if value is np.ma.masked:
            continue

        row = u'SRID=4326;POINT({lon} {lat}),{reflectivity}\n'.format(
            lon=lon[ix, iy],
            lat=lat[ix, iy],
            reflectivity=value
        )

        yield row.encode()

# And finally stream the data to CARTO
logger.info('Executing COPY command...')
result = copy_client.copyfrom(
    ('COPY nexrad_copy_example(the_geom, reflectivity)'
     ' FROM stdin WITH (FORMAT csv)'),
    rows())
logger.info(result)
