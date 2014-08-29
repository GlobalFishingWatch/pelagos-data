#!/bin/bash

# Clone the repo
git clone --recursive git@github.com:SkyTruth/pelagos.git

# Initialize GAE virutalenv
#TODO: Put this into a script in the pelagos repo
virtualenv pelagos/gae/virtualenvloader/gaevirtualenv
source pelagos/gae/virtualenvloader/gaevirtualenv/bin/activate
pip install -r pelagos/gae-requirements.txt

# Deploy
# Update app.yaml to match project
gcloud preview app deploy pelagos/gae --project skytruth-pelagos-dev
