# -*- coding: utf-8 -*-
from setuptools import setup

setup(name="carto",
    author="Daniel Carrión",
    author_email="daniel@cartodb.com",
    description="SDK around CartoDB's APIs",
    version="1.0.0",
    url="https://github.com/CartoDB/carto-python",
    packages=["carto"],
    test_suite="test.client",
    install_requires=[
        'Click',
        'requests',
        'requests-oauthlib'
    ],
    entry_points='''
        [console_scripts]
        carto=carto.cli.app:cli
    ''',
)
