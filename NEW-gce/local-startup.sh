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


# TODO: Check configfile before creating instance?  Requires user to have pelagos-data installed.


#/* ======================================================================= */#
#/*     Define PRINT_USAGE function
#/* ======================================================================= */#

function PRINT_USAGE(){

    SCRIPT_NAME=$(basename $0)
    PADDING=$(printf "\ %.0s" {1..${#SCRIPT_NAME}})

    echo ""
    echo "${SCRIPT_NAME} [-s startup.sh] [-t instance_type] [-c configfile]"
    echo "${PADDING}     [-z zone] [-n instance_name] [-i image]"
    echo ""

    return 1

}


#/* ======================================================================= */#
#/*     Define LONG_PRINT_USAGE function
#/* ======================================================================= */#

function PRINT_LONG_USAGE(){

    SCRIPT_NAME=$(basename $0)

    PRINT_USAGE
    echo "   Default machine type is n1-standard-1"
    echo ""
    echo "   Example:  ${SCRIPT_NAME} pelagos-dev-myname"
    echo "   Example:  ${SCRIPT_NAME} pelagos-dev-myname n1-highcpu-4"
    echo ""
    echo "   For more machine types, see:"
    echo "   https://cloud.google.com/compute/docs/machine-types"
    echo ""

    return 1

}


#/* ======================================================================= */#
#/*     Main Routine
#/* ======================================================================= */#


#/* ----------------------------------------------------------------------- */#
#/*     Defaults
#/* ----------------------------------------------------------------------- */#

CONFIGFILE="Config.cfg"
STARTUP_SCRIPT="remote-startup.sh"
INSTANCE_TYPE="n1-standard-1"
INSTANCE_ZONE="us-central1-a"
INSTANCE_IMAGE="pelagosdata1"
INSTANCE_NAME=
PP_CONTROLLER="pp-controller.py"


#/* ----------------------------------------------------------------------- */#
#/*     Parse arguments
#/* ----------------------------------------------------------------------- */#

ARG_ERROR=false
while [ -n "${1}" ]; do

    ARG="${1}"

    case "${ARG}" in

        "-usage" | "--usage")
            PRINT_USAGE
            exit $?
            ;;

        "-help" | "--help" | "-long-usage" | "--long-usage")
            PRINT_LONG_USAGE
            exit $?
            ;;

        "-c" | "-config")
            CONFIGFILE="$2"
            shift 2
            ;;

        "-s" | "-startup")
            STARTUP_SCRIPT="$2"
            shift 2
            ;;

        "-t" | "-type")
            INSTANCE_TYPE="$2"
            shift 2
            ;;

        "-i" | "-image")
            INSTANCE_IMAGE="$2"
            shift 2
            ;;

        "-z" | "-zone")
            INSTANCE_ZONE="$2"
            shift 2
            ;;

        "-n" | "-name")
            INSTANCE_NAME="$2"
            shift 2
            ;;

        *)
            # Catch instance name
            if [ -z "${INSTANCE_NAME}" ]; then
                INSTANCE_NAME="${ARG}"
                shift 1

            # Catch unrecognized arguments
            else
                ARG_ERROR=true
                echo "ERROR: Unrecognized argument: ${ARG}"
                shift 1
            fi
            ;;
    esac
done


#/* ----------------------------------------------------------------------- */#
#/*     Validate
#/* ----------------------------------------------------------------------- */#

BAIL=false

# Check arguments
if [ "${ARG_ERROR}" = true ]; then
    echo "ERROR: Did not successfully parse arguments"
    BAIL=true
fi

# Check startup script
if [ -z "${STARTUP_SCRIPT}" ]; then
    echo "ERROR: Need a startup script"
    BAIL=true
elif [ ! -f "${STARTUP_SCRIPT}" ]; then
    echo "ERROR: Can't find startup script: ${STARTUP_SCRIPT}"
    BAIL=true
fi

# Check configfile
if [ -z "${CONFIGFILE}" ]; then
    echo "ERROR: Need a configfile"
    BAIL=true
elif [ ! -f "${CONFIGFILE}" ]; then
    echo "ERROR: Can't find configfile: ${CONFIGFILE}"
    BAIL=true
fi

# Make sure the controller script is available
if [ "$(which ${PP_CONTROLLER})" == "" ]; then
    echo "ERROR: Utility '${PP_CONTROLLER}' isn't on path"
    BAIL=true
fi

# Found an error - exit
if [ "${BAIL}" = true ]; then
    exit 1
fi


#/* ----------------------------------------------------------------------- */#
#/*     Run startup
#/* ----------------------------------------------------------------------- */#

if [ -z "${INSTANCE_NAME}" ]; then
    INSTANCE_NAME="$(pp-controller.py get fullname)"
    EXITCODE=$?
    if [ ${EXITCODE} -ne 0 ]; then
        echo "ERROR: Tried to get instance name from configfile but received a non-zero exit code"
        echo "       Configfile result: ${INSTANCE_NAME}"
        echo "       Exit code: ${EXITCODE}"
        exit ${EXITCODE}
    fi
fi


echo ""
echo "Starting GCE instance ..."
echo "  Configfile: ${CONFIGFILE}"
echo "  Script:     ${STARTUP_SCRIPT}"
echo "  Name:       ${INSTANCE_NAME}"
echo "  Type:       ${INSTANCE_TYPE}"
echo ""


# Create the instance
gcloud  compute instances create \
    "${INSTANCE_NAME}" \
    --machine-type "${INSTANCE_TYPE}" \
    --image "${INSTANCE_IMAGE}" \
    --scopes \
        compute-rw \
        https://www.googleapis.com/auth/devstorage.full_control \
        https://www.googleapis.com/auth/bigquery \
        https://www.googleapis.com/auth/appengine.admin \
    --metadata-from-file \
        startup-script="${STARTUP_SCRIPT}" \
        configfile="${CONFIGFILE}" \
    --zone "${INSTANCE_ZONE}"

# Check to see if the gcloud command exited properly
RESULT=$(echo $?)
if [ "${RESULT}" -ne 0 ]; then
    echo "WARNING: Found a non-zero exit code for instance creation: ${RESULT}"
fi


#/* ----------------------------------------------------------------------- */#
#/*     Cleanup
#/* ----------------------------------------------------------------------- */#

echo ""
echo "Done with local startup"
echo ""

exit ${RESULT}
