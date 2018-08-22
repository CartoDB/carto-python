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
2018-08-22 11:25:18,026 - INFO - Creating table nexrad_copy_example...
2018-08-22 11:25:18,176 - INFO - Done
2018-08-22 11:25:19,787 - INFO - Avaliable datasets: ['Level2_KLVX_20180822_0910.ar2v']
2018-08-22 11:25:19,787 - INFO - Using the first one
2018-08-22 11:25:21,540 - INFO - Got the following data: Nexrad Level 2 Station KLVX from 2018-08-22T09:10:09Z to 2018-08-22T09:19:39Z
2018-08-22 11:25:21,541 - INFO - Weather Surveillance Radar-1988 Doppler (WSR-88D) Level II data are the three meteorological base data quantities: reflectivity, mean radial velocity, and spectrum width.
2018-08-22 11:25:21,541 - INFO - Pulling out some of the variables...
2018-08-22 11:25:24,494 - INFO - ref_data.shape: (720, 1832)
2018-08-22 11:25:24,494 - INFO - Converting the data...
2018-08-22 11:25:24,615 - INFO - Done
2018-08-22 11:25:24,615 - INFO - Executing COPY command...
2018-08-22 11:26:17,980 - INFO - {u'total_rows': 378947, u'time': 53.319}
```
