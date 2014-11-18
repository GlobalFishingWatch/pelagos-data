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


# General remote GCE instance startup


#/* ----------------------------------------------------------------------- */#
#/*     Updates
#/* ----------------------------------------------------------------------- */#

# Update gcloud
sudo gcloud components update -q
sudo gcloud components update gae-python -q
sudo gcloud components update app -q

# Update pip
sudo pip install pip --upgrade

echo ""
echo "Done updating"
echo ""


#/* ----------------------------------------------------------------------- */#
#/*     Run job
#/* ----------------------------------------------------------------------- */#

# Get path to an executable
JOB_PATH="$(curl -s -H "Metadata-Flavor:Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/job)"
if [ ${?} -ne 0 ]; then
    JOB_PATH=
fi

# Get executable arguments
JOB_ARGS="$(curl -s -H "Metadata-Flavor:Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/job-args)"
if [ ${?} -ne 0 ]; then
    JOB_ARGS=
fi

# No job to run
if [ -z "${JOB_PATH}" ]; then
    echo ""
    echo "No job to run"
    echo ""

# Found a path to a job that exists - execute
elif [ -f "${JOB_PATH}" ]; then
    ${JOB_PATH} ${JOB_ARGS}
    JOB_EXITCODE=$(echo $?)

# Found a path to a job that does not exist - error
elif [ ! -z "${JOB_PATH}" ] && [ ! -f "${JOB_PATH}" ]; then
    echo "ERROR: Found a job path that does not exist: ${JOB_PATH}"
fi



#/* ----------------------------------------------------------------------- */#
#/*     Terminate
#/* ----------------------------------------------------------------------- */#

# Determine if configfile says the instance should be terminated
DO_TERMINATE="$(curl -s -H "Metadata-Flavor:Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/terminate | tr '[:upper:]' '[:lower:]')"
if [ ${?} -ne 0 ]; then
    DO_TERMINATE=false
fi

# Running locally - skipping terminate
if [ "$(hostname)" == "*.local" ]; then
    echo "Running locally - skipping terminate"

# Don't terminate
elif [ "${DO_TERMINATE}" == false ]; then
    echo "Terminate set to ${DO_TERMINATE}"
    if [ ! -z ${JOB_EXITCODE} ]; then
        echo "  Job exited with: ${JOB_EXITCODE}"
    fi

# Terminate if specified and the job ran successfully
elif [ "${DO_TERMINATE}" == true ] && [ ! -z "${JOB_EXITCODE}" ] && [ ${JOB_EXITCODE} -eq 0 ]; then

    echo "Job exited with a zero - deleting instance ..."
    ZONE="$(curl -s -H 'Metadata-Flavor:Google' http://metadata.google.internal/computeMetadata/v1/instance/zone)"
    gcloud compute instances delete \
        --quiet \
        `hostname` \
        --delete-disks boot \
        --zone $(basename ${ZONE})

# Could not terminate for whatever reason
else
    echo "ERROR: Could not terminate"
    echo "       Terminate: ${DO_TERMINATE}"
    echo "       Job path:  ${JOB_PATH}"
    echo "       Job args:  ${JOB_ARGS}"
    echo "       Job exit:  ${JOB_EXITCODE}"
fi
