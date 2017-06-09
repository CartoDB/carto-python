#!/bin/bash

cd ..
pip uninstall carto -y
pip install .
cd doc
make clean && make html
