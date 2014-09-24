#!/bin/bash

if [ -z "$2" ]
  then
    echo "Usage: process_ais.sh gs://folder/input.csv.gz gs://folder/putput.csv.gz"

    exit 1
fi

IN=$1
OUT=$2

gsutil cp $IN - | gunzip -c | \
/usr/local/src/pelagos-data/utils/process_ais.py | \
gzip -c | gsutil cp - $OUT
