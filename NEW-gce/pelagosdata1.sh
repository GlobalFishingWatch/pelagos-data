#!/bin/bash


#/* ======================================================================= */#
#/*     Configure
#/* ======================================================================= */#

PROCESS_RUN="$(pp-controller.py get fullname)"
REGIONS="$(pp-controller.py get run.regions)"
RAW="$(pp-controller.py get run.process_ais_input)"
REGIONATED="$(pp-controller.py get gs_run_dir)/$(pp-controller.py get run.regionate_output)"
BQTABLE=ProcessRun."$(pp-controller.py get fullname)"
PROCESSED="$(pp-controller.py get gs_run_dir)/$(pp-controller.py get run.process_ais_output)"
BQSCHEMA="$(pp-controller.py get run.bqschema)"
LOCAL_PROCESSING_DIR="$(pp-controller.py get run.processing_dir)/$(pp-controller.py get fullname)"


#/* ======================================================================= */#
#/*     Run Updates
#/* ======================================================================= */#

# Update gcloud
sudo gcloud components update -q
sudo gcloud components update gae-python -q
sudo gcloud components update app -q

# Update pip
sudo pip install pip --upgrade

# Update the git repo
cd /usr/local/src/pelagos-data
sudo git pull
sudo pip install -r requirements.txt


#/* ======================================================================= */#
#/*     Prep workspace
#/* ======================================================================= */#

echo ""
echo "============================================="
echo "$(date) PREPPING WORKSPACE"
echo "============================================="

# Create a local processing directory and cd into it
mkdir "${LOCAL_PROCESSING_DIR}"
cd "${LOCAL_PROCESSING_DIR}"

# Get the configfile
CONIG_CONTENT="$(curl -s -H 'Metadata-Flavor:Google' http://metadata.google.internal/computeMetadata/v1/instance/attributes/configfile)"
echo "${CONFIG_CONTENT}" > "Config.cfg"
pp-controller.py check

# Create a target directory at Google Cloud Storage
gsutil mb "$(pp-controller.py get gs_run_dir)"


#/* ======================================================================= */#
#/*     Process AIS
#/* ======================================================================= */#

echo ""
echo "============================================="
echo "$(date) PROCESSING AIS"
echo "============================================="

./process_ais.sh "${RAW}" "${PROCESSED}"


#/* ======================================================================= */#
#/*     Regionate
#/* ======================================================================= */#

echo ""
echo "============================================="
echo "$(date) REGIONATING"
echo "============================================="

# Copy regions locally
gsutil cp "${REGIONS}" .

./regionate.sh "${PROCESSED}" "${REGIONATED}" "$(basename "${REGIONS}")"


#/* ======================================================================= */#
#/*     BQ Load
#/* ======================================================================= */#

echo ""
echo "============================================="
echo "$(date) LOADING BIGQUERY"
echo "============================================="

#bq load \
#    --replace \
#    --source_format=NEWLINE_DELIMITED_JSON \
#    "${BQTABLE}" \
#    "${REGIONATED}" \
#    "${BQSCHEMA}"


#/* ======================================================================= */#
#/*     Cleanup
#/* ======================================================================= */#

echo ""
echo "============================================="
echo "$(date) DONE"
echo "============================================="

