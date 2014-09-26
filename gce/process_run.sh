#!/bin/bash


RUN_DIR=`pp_controller.py get run_dir`
PROCESS_RUN=`pp_controller.py get fullname`
RAW=`pp_controller.py get raw`
REGIONS=`pp_controller.py get regions`
PROCESSED=$RUN_DIR/`pp_controller.py get processing.process_ais_output`
REGIONATED=$RUN_DIR/`pp_controller.py get processing.regionate_output`
BQTABLE=`pp_controller.py get bqtable`
BQSCHEMA=`pp_controller.py get bqschema`
SHUTDOWN=`pp_controller.py get run.shutdown`


echo ""
echo "Process run:  $PROCESS_RUN"
echo "Run dir:      $RUN_DIR"
echo "Raw:          $RAW"
echo "Regions:      $REGIONS"
echo "Processed:    $PROCESSED"
echo "Regionated:   $REGIONATED"
echo "BQTable:      $BQTABLE"
echo "BQSchema:     $BQSCHEMA"
echo "Shutdown:     $SHUTDOWN"
echo ""

exit


#PROCESS_RUN=test
#GS_BASE=gs://pelagos-data-pipeline/process-runs/$PROCESS_RUN
#RAW=gs://pelagos-data-pipeline/raw/test-2013-60k-raw-1.3.csv.gz
#PROCESSED=$GS_BASE/processed.csv.gz
#REGIONS=gs://pelagos-data-pipeline/regions/experimental/regions.sqlite
#REGIONATED=$GS_BASE/regionated.json.gz
#BQTABLE=ProcessRun.test_2013_60k_1_3__2014_09_23
#BQSCHEMA=/usr/local/src/pelagos-data/schema/scored-ais-processed-schema-1.4.json


echo ""
echo "$(date) PROCESSING AIS"
echo "============================================="

./process_ais.sh $RAW $PROCESSED

echo ""
echo "$(date) REGIONATING"
echo "============================================="

gsutil cp $REGIONS .

./regionate.sh $PROCESSED $REGIONATED

echo ""
echo "$(date) LOADING BIGQUERY"
echo "============================================="

bq load --replace --source_format=NEWLINE_DELIMITED_JSON $BQTABLE $REGIONATED $BQSCHEMA

echo ""
echo "$(date) DONE"
echo "============================================="


if [ "`hostname`" != "*.local" ]; then
    echo "Deleting instance"
    gcutil deleteinstance -f `hostname` --nodelete_boot_pd
    echo "Done."
else
    echo "Running locally - skipping delete instance"
fi

exit 0
