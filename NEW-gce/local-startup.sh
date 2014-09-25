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

if [ -z "$1" ]
  then
    echo ""
    echo "Usage: $0 INSTANCE_NAME [MACHINE_TYPE]"
    echo ""
    echo "   Default machine type is n1-standard-1"
    echo ""
    echo "   Example:  $0 pelagos-dev-myname"
    echo "   Example:  $0 pelagos-dev-myname n1-highcpu-4"
    echo ""
    echo "   For more machine types, see "
    echo "   https://cloud.google.com/compute/docs/machine-types"
    exit 1
fi

NAME=$1

if [ -z "$2" ]; then
  TYPE="n1-standard-1"
else
  TYPE=$2
fi

SCRIPT="remote-startup.sh"

echo "Starting GCE instance $NAME as $TYPE"
echo "Using startup script $SCRIPT"
echo ""

# Create the instance
gcutil \
    addinstance \
    $NAME \
    --machine_type=$TYPE \
    --image=pelagosdata1 \
    --service_account_scope=compute-rw,https://www.googleapis.com/auth/devstorage.full_control,https://www.googleapis.com/auth/bigquery,https://www.googleapis.com/auth/appengine.admin \
    --metadata_from_file=startup-script:$SCRIPT \
    --zone=us-central1-a

echo "Done with local startup"
