#!/usr/bin/env python


# This document is part of the pelagos project
# https://github.com/skytruth/pelagos


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


"""
Sample code showing how to classify a CSV
"""


import csv
import json
from os.path import *
import sys

import putils


#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#

__docname__ = basename(__file__)


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    print("""
Usage: {0} polygon_layer.shp input.csv output.csv
    """.format(__docname__))

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse arguments
    #/* ----------------------------------------------------------------------- */#

    # Get input files
    polygon_file = args[0]
    input_csv_file = args[1]
    output_csv_file = args[2]

    if isfile(output_csv_file):
        print("ERROR: Output CSV file already exists: %s" % output_csv_file)
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prep polygon layer
    #/* ----------------------------------------------------------------------- */#

    # Open polygon layer for reading
    # Arguments are file path and layer name
    # Unfortunately a layer cannot exist without an open datasource so both objects must exist
    poly_ds, poly_layer = putils.io.open_datasource(polygon_file, basename(polygon_file).split('.')[0])

    #/* ----------------------------------------------------------------------- */#
    #/*     Prep input CSV
    #/* ----------------------------------------------------------------------- */#

    # Figure out how many data rows are in the input CSV
    num_rows = None
    with open(input_csv_file, 'r') as f:
        num_rows = len([i for i in csv.DictReader(f)])

    # Set up CSV reader
    output_csv_rows = []
    with open(input_csv_file, 'r') as i_f:
        reader = csv.DictReader(i_f)

        #/* ----------------------------------------------------------------------- */#
        #/*     Prep output CSV
        #/* ----------------------------------------------------------------------- */#

        # Set up writer
        fieldnames = reader.fieldnames + ['FIDS', 'attributes']
        with open(output_csv_file, 'w') as o_f:
            writer = csv.DictWriter(o_f, fieldnames=fieldnames)
            writer.writeheader()

            # Process all rows of input CSV
            row_counter = 0
            for row in reader:

                # Update user
                row_counter += 1
                sys.stdout.write("\r\x1b[K" + "    %s/%s" % (str(row_counter), str(num_rows)))
                sys.stdout.flush()

                # Get the attributes for all intersecting features
                latitude = row['lat']
                longitude = row['long']
                intersecting_attributes = putils.classify.get_all_intersecting_attributes(longitude, latitude,
                                                                                          poly_layer)

                # Modify row for writing purposes
                row['FIDS'] = json.dumps(intersecting_attributes.keys())
                row['attributes'] = json.dumps(intersecting_attributes)

                # Write the row with additional attributes to the output file
                writer.writerow(row)

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    # IMPORTANT: Close OGR objects
    # Objects must be closed in a hierarchical order (geometry, feature, layer, datasource)
    # or Python will crash if an object is used and its parent doesn't exist
    # There are of course exceptions to this rule

    poly_layer = None
    poly_ds = None

    print(" - Done")
    return 1


#/* ======================================================================= */#
#/*     Commandline Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Not enough arguments - print usage
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - give all but the first to the main() function
    else:
        sys.exit(main(sys.argv[1:]))
