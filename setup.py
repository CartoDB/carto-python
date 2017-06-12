# -*- coding: utf-8 -*-
from setuptools import setup

try:
    with open('requirements.txt') as f:
        required = f.read().splitlines()
except:
    required = ['requests>=2.7.0', 'pyrestcli>=0.6.3']

try:
    with open('test_requirements.txt') as f:
        test_required = f.read().splitlines()
except:
    pass

setup(name="carto",
      author="Daniel Carrión",
      author_email="daniel@carto.com",
      description="SDK around CARTO's APIs",
      version="1.0.1",
      url="https://github.com/CartoDB/carto-python",
      install_requires=required,
      packages=["carto"])
