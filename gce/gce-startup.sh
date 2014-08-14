#!/bin/bash

echo "source /usr/local/share/google/google-cloud-sdk/path.bash.inc" >> /etc/profile
echo "source /usr/local/share/google/google-cloud-sdk/completion.bash.inc" >> /etc/profile

sudo apt-get update
sudo apt-get install git -y
sudo apt-get install python-pip -y
sudo apt-get install zip unzip


sudo pip install nose
sudo pip install docopt

cd /usr/local/src
git clone https://github.com/SkyTruth/pelagos-data.git

