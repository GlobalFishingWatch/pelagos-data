#!/usr/bin/env python


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


"""
Components for commandline utilities
"""


import csv
import inspect
import os
from os.path import *
import sys


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__docname__ = basename(inspect.getfile(inspect.currentframe()))
__all__ = ['print_usage', 'main']


#/* ======================================================================= */#
#/*     Define global variables
#/* ======================================================================= */#

UTIL_NAME = __docname__


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
{0} [--usage] [-mf mmsi_field] [-cf compare_field]  [-omf o_mmsi_field]
{1} [--overwrite] input_csv1 input_csv2 [input_csv...] output_file
    """.format(UTIL_NAME, ' ' * len(UTIL_NAME)))

    return 1


#/* ======================================================================= */#
#/*     Define file2dict() function
#/* ======================================================================= */#

def file2dict(primary_field, ifile):

    output = {}
    with open(ifile, 'r') as f:
        reader = csv.DictReader(f)
        if primary_field not in reader.fieldnames:
            raise ValueError("primary_field '%s' not in input file field names: %s"
                             % (primary_field, ', '.join(reader.fieldnames)))
        for row in reader:
            primary_val = row[primary_field]
            output[primary_val] = row.copy()

    return output.copy()


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):


    # Print usage
    if len(args) is 0:
        return print_usage()


    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    mmsi_field = 'mmsi'
    compare_field = 'v_imo'
    o_mmsi_field = 'mmsi'
    overwrite_mode = False

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    input_csv_files = []
    output_csv_file = None

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse Arguments
    #/* ----------------------------------------------------------------------- */#

    i = 0
    arg = None
    arg_error = False
    while i < len(args):

        try:
            arg = args[i]

            # Configure input file
            if arg in ('-mf', '-mmsi-field'):
                i += 2
                mmsi_field = args[i - 1]
            elif arg in ('-cf', '-compare-field'):
                i += 2
                compare_field = args[i - 1]

            # Configure output file
            elif arg in ('-omf', '-ommsi-field'):
                i += 2
                o_mmsi_field = args[i - 1]

            # Additional options
            elif arg == '--overwrite':
                i += 1
                overwrite_mode = True

            # Positional arguments and errors
            else:

                # Assume all other arguments are input files to be compared
                i += 1
                input_csv_files.append(expanduser(arg))

        except (IndexError, ValueError):
            arg_error = True
            print("ERROR: An argument has invalid parameters - current arg: %s\n" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate configuration / transform arguments
    #/* ----------------------------------------------------------------------- */#

    # Get the output file
    try:
        output_csv_file = input_csv_files.pop(-1)
    except IndexError:
        output_csv_file = None

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check input files
    if len(input_csv_files) < 2:
        bail = True
        print("ERROR: Need at least 2 input files - received %s" % len(input_csv_files))
    for ifile in input_csv_files:
        if not os.access(ifile, os.R_OK):
            bail = True
            print("ERROR: Can't access input file: %s" % ifile)
        else:
            with open(ifile, 'r') as f:
                reader = csv.DictReader(f)
                if mmsi_field not in reader.fieldnames:
                    bail = True
                    print("ERROR: Input file missing MMSI field '%s': %s" % (mmsi_field, ifile))
                if compare_field not in reader.fieldnames:
                    bail = True
                    print("ERROR: Input file missing compare field '%s': %s" % (compare_field, ifile))

    # Check output file
    if output_csv_file is None:
        bail = True
        print("ERROR: Need an output CSV file")
    elif not overwrite_mode and isfile(output_csv_file):
        bail = True
        print("ERROR: Overwrite=%s and output file exists: %s" % (overwrite_mode, output_csv_file))

    # Found an error - exit
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Update user
    #/* ----------------------------------------------------------------------- */#

    print("Input files:")
    for ifile in input_csv_files:
        print("    %s" % ifile)
    print("Output file:")
    print("    %s" % output_csv_file)

    #/* ----------------------------------------------------------------------- */#
    #/*     Get unique list of MMSI numbers
    #/* ----------------------------------------------------------------------- */#

    bail = False
    unique_mmsi = []
    print("Getting a unique list of MMSI values ...")
    for ifile in input_csv_files:
        with open(ifile, 'r') as f:
            reader = csv.DictReader(f)
            sub_mmsi = []
            for row in reader:
                mmsi = row[mmsi_field]
                if mmsi not in sub_mmsi:
                    sub_mmsi.append(mmsi)
                else:
                    bail = True
                    print("    ERROR: MMSI '%s' appears multiple times in: %s" % (mmsi, ifile))
            unique_mmsi += sub_mmsi
    unique_mmsi = list(set(unique_mmsi))
    unique_mmsi.sort()
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Cache input files
    #/* ----------------------------------------------------------------------- */#

    # Convert input files to dictionaries with MMSI values as keys for more efficient data access
    print("Caching input files ...")
    cache = {ifile: file2dict(mmsi_field, ifile) for ifile in input_csv_files}

    #/* ----------------------------------------------------------------------- */#
    #/*     Compare input files
    #/* ----------------------------------------------------------------------- */#

    # Process
    no_match_count = 0
    prog_i = 0
    prog_max = len(unique_mmsi)
    print("Comparing records ...")
    with open(output_csv_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=[o_mmsi_field])
        writer.writeheader()
        for mmsi in unique_mmsi:

            # Update user
            prog_i += 1
            sys.stdout.write("\r\x1b[K" + "    %s/%s" % (str(prog_i), str(prog_max)))
            sys.stdout.flush()
            compare_list = []
            for ifile in input_csv_files:
                try:
                    compare_val = cache[ifile][mmsi][compare_field]
                    if compare_val:
                        compare_list.append(compare_val)
                except KeyError:
                    pass
            if compare_list and len(set(compare_list)) is not 1:
                no_match_count += 1
                writer.writerow({o_mmsi_field: mmsi})
    print(" - Done")
    print("Found %s non-matching records" % no_match_count)

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and final return
    #/* ----------------------------------------------------------------------- */#

    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Remove script name and give the rest to main
    sys.exit(main(sys.argv[1:]))
