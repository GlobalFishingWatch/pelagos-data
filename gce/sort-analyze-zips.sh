#!/bin/bash


OUTPUT=sorted.csv.gz
rm $OUTPUT

# Add csv header to the output file
gzip -c /usr/local/src/pelagos-data/schema/scored-ais-raw-schema-1.3.csv > $OUTPUT

for Z in unsorted/*.zip
do
  rm -rf temp
  mkdir temp
  echo "Unzipping $Z"
  unzip -j $Z -d temp
  echo ""
  echo "Sorting..."
  for F in temp/*
  do
    echo "  $(date) $F"
    sort -t"," -k4,4n $F | gzip -c >> $OUTPUT
  done
done

rm -rf temp
