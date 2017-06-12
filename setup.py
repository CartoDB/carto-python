# -*- coding: utf-8 -*-
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('test_requirements.txt') as f:
    test_required = f.read().splitlines()

setup(name="carto",
      author="Daniel Carrión",
      author_email="daniel@carto.com",
      description="SDK around CartoDB's APIs",
      version="1.0.0",
      url="https://github.com/CartoDB/carto-python",
      install_requires=required,
      packages=["carto"])
