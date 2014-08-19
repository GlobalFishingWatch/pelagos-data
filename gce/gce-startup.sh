#!/bin/bash

#echo "source /usr/local/share/google/google-cloud-sdk/path.bash.inc" >> /etc/profile
#echo "source /usr/local/share/google/google-cloud-sdk/completion.bash.inc" >> /etc/profile
#
#sudo apt-get update
#sudo apt-get install gcc python-dev python-setuptools -y
#sudo apt-get install git -y
#sudo apt-get install python-pip -y
#sudo apt-get install zip unzip
#sudo apt-get install python-gdal -y
#
#sudo pip install -U crcmod
#
#cd /usr/local/src
#sudo git clone https://github.com/SkyTruth/pelagos-data.git
#sudo pip install -r ./pelagos-data/requirements.txt


# New startup script (much tidier :-)
cd /usr/local/src/pelagos-data
sudo git pull
sudo pip install -r requirements.txt



