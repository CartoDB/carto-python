## Submitting Contributions

Contributions are totally welcome. However, contributors must sign a Contributor License Agreement (CLA) before making a submission. [Learn more here.](https://carto.com/contributing)

## Release process

1. You must be maintainer at [carto pypi repo](https://pypi.python.org/pypi/carto/).
2. Prepare a `~/.pypirc` file:

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

3. Upload the package to the test repository: `python setup.py sdist upload -r pypitest`.
4. Install it in a new environment: `pip install --index-url=https://test.pypi.org/simple --extra-index-url=https://pypi.org/simple carto`.
5. Test it.
6. Release it: `python setup.py sdist upload -r pypi`.
