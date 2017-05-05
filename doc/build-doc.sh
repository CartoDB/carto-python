#!/bin/bash

cd ..
pip uninstall carto
pip install .
cd doc
make clean && make html
