#!/bin/bash

# pull down the raw data file
gsutil cp gs://analyze-data/raw/atw2_20k-raw.csv.gz .

# Process
gunzip -c atw2_20k-raw.csv.gz | /usr/local/src/pelagos-data/utils/process_ais.py | gzip -c > atw2_20k-processed.csv.gz

# upload it
gsutil cp atw2_20k-processed.csv.gz gs://analyze-data/processed


# load into BigQuery
bq load --skip_leading_rows=1 --max_bad_records=100 \
    Global_20k_2012.processed_1_3 gs://analyze-data/processed/atw2_20k-processed.csv.gz \
    /usr/local/src/pelagos-data/schema/scored-ais-processed-schema-1.3.json
