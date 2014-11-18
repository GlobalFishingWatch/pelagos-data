#!/bin/bash

PROCESS_RUN=kwurster_20141003_oceana_2
GS_BASE=gs://pelagos-data-pipeline/process-runs/$PROCESS_RUN
RAW=gs://pelagos-data-pipeline/raw/atw3_20k-raw.csv.gz
PROCESSED=$GS_BASE/processed.csv.gz
REGIONS=gs://pelagos-data-pipeline/regions/oceana-report-regions.sqlite
REGIONATED=$GS_BASE/regionated.json.gz
BQTABLE=ProcessRun.$PROCESS_RUN
BQSCHEMA=scored-ais-processed-schema-1.4.json

echo ""
echo $PROCESS_RUN
echo $REGIONS
echo $RAW
echo $REGIONATED
echo $BQTABLE
echo $PROCESSED
echo $BQSCHEMA
echo ""
exit

echo ""
echo "$(date) PROCESSING AIS"
echo "============================================="

#./process_ais.sh $RAW $PROCESSED

echo ""
echo "$(date) REGIONATING"
echo "============================================="

#gsutil cp $REGIONS .

#./regionate.sh $PROCESSED $REGIONATED

echo ""
echo "$(date) LOADING BIGQUERY"
echo "============================================="

bq load --replace --source_format=NEWLINE_DELIMITED_JSON $BQTABLE $REGIONATED $BQSCHEMA

echo ""
echo "$(date) DONE"
echo "============================================="