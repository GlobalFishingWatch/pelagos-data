#!/bin/bash

# Startup script for image pelagosdata1
# https://console.developers.google.com/project/apps~skytruth-pelagos-dev/compute/imagesDetail/global/images/pelagosdata1

#TODO: set up images so that is pulls the latest pelagos-data commit and then runs a
# setup script in from the repo.  The startup script passed to the instance just does that.
# Accumulate new changes to the instance in the second script, and every once in a while
# make a new image that contains all those changes

sudo gcloud components update -q
sudo gcloud components update gae-python -q
sudo gcloud components update app -q

sudo pip install virtualenv

cd /usr/local/src/pelagos-data
sudo git pull
sudo pip install -r requirements.txt




