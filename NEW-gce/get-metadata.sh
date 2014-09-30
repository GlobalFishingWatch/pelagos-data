#!/bin/bash


# This document is part of pelagos-data
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


# Usage
if [ -z "$1" ] || [ "$1" == "-usage" ] || [ "$1" == "--usage" ] || [ "$1" == "-help" ] || [ "$1" == "--help" ]; then

    echo ""
    echo "$(basename $0) KEY [TARGET_FILE]"
    echo ""

    exit 1
fi


# Parse arguments
KEY="$1"
if [ -z "$2" ]; then
    TARGET_FILE=
else
    TARGET_FILE="$2"
fi


# Make sure the target file doesn't exist
if [ ! -z "$TARGET_FILE" ] && [ -e $"TARGET_FILE" ]; then
    echo ""
    echo "ERROR: Target file exists: $TARGET_FILE"
    exit 1
fi


# Get the metadata value
VALUE=$(curl -s -H "Metadata-Flavor:Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/${KEY})


# Dump the value
if [ ! -z "$TARGET_FILE" ]; then
    echo "${VALUE}\n" > ${TARGET_FILE}
else
    printf "${VALUE}"
fi

exit 0
