#!/bin/bash


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

if [ -z "$2" ]
then
  TYPE=n1-standard-1
else
  TYPE=$2
fi

SCRIPT=./gce-startup.sh

echo "Starting GCE instance $NAME as $TYPE"
echo "Using startup script $SCRIPT"
echo ""

gcutil addinstance $NAME  --machine_type=$TYPE    --image=pelagosdata1    --service_account_scope=https://www.googleapis.com/auth/devstorage.full_control,https://www.googleapis.com/auth/bigquery,https://www.googleapis.com/auth/appengine.admin    --metadata_from_file=startup-script:$SCRIPT    --zone=us-central1-a

