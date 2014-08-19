
sudo apt-get install build-essential python-all-dev libsqlite3-dev libspatialite-dev libgeos-dev -y

wget http://download.osgeo.org/gdal/1.11.0/gdal-1.11.0.tar.gz
tar xvfz gdal-1.11.0.tar.gz
cd gdal-1.11.0

./configure --with-python --with-spatialite=yes --with-libgeos=yes
make
sudo make install



export "LD_LIBRARY_PATH=/usr/local/lib"

or

 sudo ldconfig ???