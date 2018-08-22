# NEXRAD `copyfrom` example

This is an example of how to use the `CopySQLClient` class and the SQL
API to stream data from a service to a table. In this case we stream
data from the NEXRAD radar data service.

This shows a method that can be used to ingest near real-time
data. Beautiful RADAR data that can also produce beautiful
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
virtualenv env
source env/bin/activate
pip install -r requirements.txt
export CARTO_API_URL=https://YOUR_USER_NAME.carto.com/
export CARTO_API_KEY=YOUR_API_KEY
```

## Usage

```sh
python nexrad_copy.py -h
```
