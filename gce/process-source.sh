#!/bin/bash

# Process source files form analyze
gsutil cp gs://analyze-data/source/atw2_20k/*.zip .
unzip -p "*.zip" | cat /usr/local/src/pelagos-data/schema/scored-ais-raw-schema-1.3.csv - | gzip >  atw2_20k-raw.csv.gz
gsutil cp *.csv.gz gs://analyze-data/raw

# load raw data ino bigquery
bq load --skip_leading_rows=1 --max_bad_records=100 \
    Global_20k_2012.raw_1_3 gs://analyze-data/raw/atw2_20k-raw.csv.gz \
    /usr/local/src/pelagos-data/schema/scored-ais-raw-schema-1.3.json

