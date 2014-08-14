#!/bin/bash

# pull down the raw data file
gsutil cp gs://analyze-data/raw/atw2_20k-raw.csv.gz .

#unzip it.  TODO: change the proccess_ais script so it can read from stdin, then we can stream the file directly through it
gunzip atw2_20k-raw.csv.gz

# process it. TODO: add shebang to  process_ais.  Make sure it works in virtualenv properly
python /usr/local/src/pelagos-data/utils/process_ais.py  atw2_20k-raw.csv  atw2_20k-processed.csv

# upload it
gsutil cp atw2_20k-processed.csv gs://analyze-data/raw/processed
