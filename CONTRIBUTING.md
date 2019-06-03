## Submitting Contributions

Contributions are totally welcome. However, contributors must sign a Contributor License Agreement (CLA) before making a submission. [Learn more here.](https://carto.com/contributing)

## Release process

1. Make sure documentation is generated properly. See the [doc](https://github.com/CartoDB/carto-python/tree/master/doc) directory for more information.
2. Update version number and information at `setup.py`, `conf.py` and `NEWS.md`.
3. You must be maintainer at [carto pypi repo](https://pypi.python.org/pypi/carto/).
4. Prepare a `~/.pypirc` file:

```
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
username=your_username
password=your_password

[pypitest]
username=your_username
password=your_password
```

5. Release it: `python setup.py sdist upload -r pypi`.
