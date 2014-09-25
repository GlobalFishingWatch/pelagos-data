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


# Return home and run processing script
cd ~/
process-controller.py
EXITCODE=$?


# Exit code is 0 but script is running locally and not on a GCE instance
if [ "`hostname`" == "*.local" ] && [ $EXITCODE -eq 0 ]; then
    echo "Found zero exit code, but running locally - skipping deleteinstance"
    exit 0

# Exit code is 0 - delete instance
elif [ $EXITCODE -eq 0 ]; then
    echo "Found zero exit code - deleting instance ..."
    gcutil deleteinstance -f `hostname` --nodelete_boot_pd
    exit $EXITCODE

# Non-zero exit code - just exit
else
    echo "ERROR: Found a non-zero exit code - skipping shutdown"
    exit $EXITCODE
fi
