#!/bin/bash

# Download dependencies
sudo apt-get install build-essential python-all-dev libsqlite3-dev libspatialite-dev libgeos-dev libgdal1-dev -y

# Get source
wget http://download.osgeo.org/gdal/1.11.0/gdal-1.11.0.tar.gz
tar xvfz gdal-1.11.0.tar.gz
cd gdal-1.11.0

./configure \
    --with-python \
    --with-spatialite=YES \
    --with-libgeos=YES \
    --with-ogr

# Make on all cores
make -j `sysctl -n hw.ncpu`
sudo make install

echo "Testing GEOS ..."
./test-geos.py
