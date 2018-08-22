# NEXRAD `copyfrom` example

This is an example of how to use the `CopySQLClient` class and the SQL
API to stream data from a service to a table. In this case we stream
data from the NEXRAD radar data service.

This shows a method that can be used to ingest near real-time
data. Beautiful radar data that can also produce beautiful
visualizations.

![NEXRAD example](./nexrad_example.png)

For more information about this service and the implementations that
inspired this example, please see:

- https://carto.com/blog/mapping-nexrad-radar-data/
- https://gist.github.com/stuartlynn/a7868cf8ca02931a6408
- http://nbviewer.jupyter.org/gist/dopplershift/356f2e14832e9b676207


## Installation

```sh
cd carto-python/examples/nexrad
virtualenv env # or virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
export CARTO_API_URL=https://YOUR_USER_NAME.carto.com/
export CARTO_API_KEY=YOUR_API_KEY
```

## Usage

```sh
$ python nexrad_copy.py -h
```

```
$ python nexrad_copy.py
INFO:nexrad_copy:Creating table nexrad_copy_example...
INFO:nexrad_copy:Done
INFO:nexrad_copy:Trying to connect to the THREDDS radar query service
INFO:nexrad_copy:Quering data from the station
INFO:nexrad_copy:Avaliable datasets: ['Level2_KLVX_20180822_1536.ar2v']
INFO:nexrad_copy:Using the first one
INFO:nexrad_copy:Got the following data: Nexrad Level 2 Station KLVX from 2018-08-22T15:36:10Z to 2018-08-22T15:40:41Z
INFO:nexrad_copy:Weather Surveillance Radar-1988 Doppler (WSR-88D) Level II data are the three meteorological base data quantities: reflectivity, mean radial velocity, and spectrum width.
INFO:nexrad_copy:Pulling out some of the variables...
INFO:nexrad_copy:ref_data.shape: (720, 1832)
INFO:nexrad_copy:Converting the data...
INFO:nexrad_copy:Done
INFO:nexrad_copy:Executing COPY command...
INFO:nexrad_copy:{u'total_rows': 204789, u'time': 28.805}
```
