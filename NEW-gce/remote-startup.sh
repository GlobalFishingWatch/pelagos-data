#!/bin/bash


# This document is part of Pelagos Data
# https://github.com/skytruth/pelagos-data


# =========================================================================== #
#
#  The MIT License (MIT)
#
#  Copyright (c) 2014 SkyTruth
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
# =========================================================================== #


# Startup script for image pelagosdata1
# https://console.developers.google.com/project/apps~skytruth-pelagos-dev/compute/imagesDetail/global/images/pelagosdata1


#/* ----------------------------------------------------------------------- */#
#/*     Setup requirements
#/* ----------------------------------------------------------------------- */#

# Make sure Google Cloud Components are up to date
sudo gcloud components update -q
sudo gcloud components update gae-python -q
sudo gcloud components update app -q

# Pull processing repo
cd /usr/local/src/pelagos-data
sudo git pull

# Make sure pip is up to date, install requirements, and install repo
sudo pip install pip --upgrade
sudo pip install -r requirements.txt
sudo pip install . --upgrade


#/* ----------------------------------------------------------------------- */#
#/*     Process data
#/* ----------------------------------------------------------------------- */#

# Return home and run processing script
cd ~/
process-controller.py
EXITCODE=$($?)


#/* ----------------------------------------------------------------------- */#
#/*     Determine whether instance should be shut down
#/* ----------------------------------------------------------------------- */#

# Determine if configfile says the instance should be terminated
DO_TERMINATE=$(pp_controller.py get run.shutdown | tr '[:upper:]' '[:lower:]')

# Configfile explicitly says do not delete
if [ "${DO_TERMINATE}" == false ]; then
    echo "Configfile prevents instance shutdown - skipping"

# Script running locally - skip shutdown
elif [ "$(hostname)" == "*.local" ]; then
    echo "Running locally - skipping delete instance"

# Exit code is 0 - delete instance
elif [ ${EXITCODE} -eq 0 ]; then
    echo "Found zero exit code - deleting instance ..."

    # In order to auto-agree to the prompts, use --quiet
    gcloud compute instances delete \
        --quiet \
        `hostname` \
        --keep-disks boot \
        --delete-disks data \
        --zone $(basename `curl -s -H "Metadata-Flavor:Google" http://metadata.google.internal/computeMetadata/v1/instance/zone`)

# Non-zero exit code - just exit
else
    echo "ERROR: Found a non-zero exit code - skipping delete instance"
fi


#/* ----------------------------------------------------------------------- */#
#/*     Cleanup
#/* ----------------------------------------------------------------------- */#

# Exit
if [ ${EXITCODE} -ne 0 ]; then
    echo "WARNING: Found non-zero exit code: ${EXITCODE}"
fi

exit ${EXITCODE}
