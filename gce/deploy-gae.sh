#!/bin/bash

# Clone the repos
git clone --recursive git@github.com:SkyTruth/pelagos.git
git clone --recursive git@github.com:SkyTruth/pelagos-data.git

# Initialize GAE virutalenv
#TODO: Put this into a script in the pelagos repo
virtualenv pelagos/gae/virtualenvloader/gaevirtualenv
source pelagos/gae/virtualenvloader/gaevirtualenv/bin/activate
pip install -r pelagos/gae-requirements.txt

# Deploy
# Update app.yaml to match project
gcloud preview app deploy pelagos/gae --project skytruth-pelagos-dev

#Upload vessselinfo (will prompt for password)
#TODO: direct log files cfreated by uploader to a tempfolder and cleanup afterward
appcfg.py upload_data --config_file=./pelagos-data/data/vesselinfo/vesselinfo-bulkloader.yaml \
--filename=./pelagos-data/data/vesselinfo/vessel-info-2014-08-28.csv --kind=VesselInfo \
--num_threads=4 --url=http://skytruth-pelagos-dev.appspot.com/_ah/remote_api  \
--rps_limit=500 --email=paul@skytruth.org
