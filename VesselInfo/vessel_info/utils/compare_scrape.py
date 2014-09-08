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
Compare mmsi2info.py output to determine which sources produce differing results
"""


from __future__ import print_function
from __future__ import unicode_literals

import csv
import inspect
import os
from os import linesep
from os.path import *
import sys

from common import *


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__docname__ = basename(inspect.getfile(inspect.currentframe()))
__all__ = ['print_help', 'print_usage', 'print_long_usage', 'file2dict', 'main']


#/* ======================================================================= */#
#/*     Define global variables
#/* ======================================================================= */#

UTIL_NAME = __docname__
VERBOSE_MODE = True


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    vprint("""
{0} [--usage] [-mf mmsi_field] [-cf compare_field]  [-omf o_mmsi_field]
{1} [--overwrite] input_csv1 input_csv2 [input_csv...] output_file
    """.format(UTIL_NAME, ' ' * len(UTIL_NAME)))

    return 1


#/* ======================================================================= */#
#/*     Define print_long_usage() function
#/* ======================================================================= */#

def print_long_usage():

    """
    Print full commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print_usage()
    vprint("""Options:
    -mf -mmsi-field     Field in all input files containing MMSI numbers
                        [default: mmsi]
    -cf -compare-field  Field in all input files that will be compared
                        [default: v_imo]
    -omf -ommsi-field   Name of MMSI field in output file
                        [default: mmsi]
    --overwrite         Blindly overwrite output file if it exists
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_help():

    """
    Print commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    vprint("""
Help: {0}
------{1}""".format(UTIL_NAME, '-' * len(UTIL_NAME)))
    vprint(main.__doc__)

    return 1


#/* ======================================================================= */#
#/*     Define file2dict() function
#/* ======================================================================= */#

def file2dict(primary_field, ifile):

    """

    """

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
#/*     Define vprint() function
#/* ======================================================================= */#

def vprint(message, stream=sys.stdout):
    
    """
    Easily handle verbose printing
    
    :param message: single or multi-line message to be printed
    :type message: str|unicode|list|tuple
    """
    
    global VERBOSE_MODE
    
    if VERBOSE_MODE:
        
        # Message is multiple lines
        if isinstance(message, (list, tuple)):
            for line in message:
                
                # Figure out if a newline character is needed, modify, then write
                if line[-1] != linesep:
                    line += linesep
                stream.write(line)
        
        # Message is a single line
        else:
            # Figure out if a newline character is needed, modify, then write
            if message[-1] != linesep:
                message += linesep
            stream.write(message)
            

#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
Compare output files generated by mmsi2info.py to determine whether or not a
given MMSI has matching values.  This is useful to determine which vessels
have changed names or which websites have differing information.

By default the 'v_imo' field is compared but any field present in all output
files can be compared with the '-compare-field' flag.

In order to determine whether or not a given record matches, the input files are
first opened and a unique set of MMSI numbers is generated based on all documents.
The values for each MMSI and field being compared are extracted from all input
files and compared if they are not null.  If input file 1 and 2 have a value
but input file 3 does not, then only the values from input files 1 and 2 are
compared.  If the values are not identical then the MMSI number is written to
the output file.  If one of the input files contains extra MMSI numbers that
do not appear in any of the other files, these values will NOT be written to
the output file.


Exit codes:
    0 on success
    1 on failure


Input file requirements:
    1. Need at least two files
    2. All files must have the same MMSI field
    3. All fields must have the field being compared


Sample Commands
---------------

Compare vessel names for all scrapers

    $ compare_scrape.py \\
        -cf v_name \\
        VesselFinder.csv \\
        FleetMON.csv \\
        MarineTraffic.csv \\
        Conflicts.csv


Compare vessel names for all scrapers but use non-default MMSI fields

    $ compare_scrape.py \\
        -cf v_name \\
        -mf MMSI_Number \\
        -omf Conflict_MMSI \\
        VesselFinder.csv \\
        FleetMON.csv \\
        MarineTraffic.csv \\
        Conflicts.csv
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    # Print usage
    if len(args) is 0:
        return print_usage()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#
    
    global VERBOSE_MODE

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

            # Help arguments
            if arg in ('--help', '-help'):
                return print_help()
            elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo', '-h'):
                return print_help_info()
            elif arg in ('--license', '-license'):
                return print_license()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--short-version', '-short-version'):
                return print_short_version()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--long-usage', '-long-usage'):
                return print_long_usage()
            
            # User feedback
            elif arg in ('-q', '-quiet'):
                i += 1
                VERBOSE_MODE = False

            # Configure input file
            elif arg in ('-mf', '-mmsi-field'):
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
            vprint("ERROR: An argument has invalid parameters - current arg: %s" % arg)

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
        vprint("ERROR: Did not successfully parse arguments")

    # Check input files
    if len(input_csv_files) < 2:
        bail = True
        vprint("ERROR: Need at least 2 input files - received %s" % len(input_csv_files))
    for ifile in input_csv_files:
        if not os.access(ifile, os.R_OK):
            bail = True
            vprint("ERROR: Can't access input file: %s" % ifile)
        else:
            with open(ifile, 'r') as f:
                reader = csv.DictReader(f)
                if mmsi_field not in reader.fieldnames:
                    bail = True
                    vprint("ERROR: Input file missing MMSI field '%s': %s" % (mmsi_field, ifile))
                if compare_field not in reader.fieldnames:
                    bail = True
                    vprint("ERROR: Input file missing compare field '%s': %s" % (compare_field, ifile))

    # Check output file
    if output_csv_file is None:
        bail = True
        vprint("ERROR: Need an output CSV file")
    elif not overwrite_mode and isfile(output_csv_file):
        bail = True
        vprint("ERROR: Overwrite=%s and output file exists: %s" % (overwrite_mode, output_csv_file))

    # Found an error - exit
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Update user
    #/* ----------------------------------------------------------------------- */#

    vprint("Input files:")
    for ifile in input_csv_files:
        vprint("    %s" % ifile)
    vprint("Output file:")
    vprint("    %s" % output_csv_file)

    #/* ----------------------------------------------------------------------- */#
    #/*     Get unique list of MMSI numbers
    #/* ----------------------------------------------------------------------- */#

    bail = False
    unique_mmsi = []
    vprint("Getting a unique list of MMSI values ...")
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
                    vprint("    ERROR: MMSI '%s' appears multiple times in: %s" % (mmsi, ifile))
            unique_mmsi += sub_mmsi
    unique_mmsi = list(set(unique_mmsi))
    unique_mmsi.sort()
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Cache input files
    #/* ----------------------------------------------------------------------- */#

    # Convert input files to dictionaries with MMSI values as keys for more efficient data access
    vprint("Caching input files ...")
    cache = {ifile: file2dict(mmsi_field, ifile) for ifile in input_csv_files}

    #/* ----------------------------------------------------------------------- */#
    #/*     Compare input files
    #/* ----------------------------------------------------------------------- */#

    # TODO: Allow user to compare an arbitrary number of fields
    # Use the following data structure:
    #
    #   {
    #       'compare_field1': ['icsv1_val', 'icsv2_val', 'icsv2_val'],
    #       'compare_field2': ['icsv1_val', 'icsv2_val', 'icsv2_val']
    #   }
    #
    # If all of the lists match, then don't write the MMSI to the output value

    # Process
    num_match_count = 0
    prog_i = 0
    prog_max = len(unique_mmsi)
    vprint("Comparing records ...")
    with open(output_csv_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=[o_mmsi_field])
        writer.writeheader()
        for mmsi in unique_mmsi:

            # Update user
            prog_i += 1
            if VERBOSE_MODE:
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
            # TODO: If 3 input files are specified and only one of them has a value in the column being compared, this is where it gets excluded
            if compare_list and len(set(compare_list)) is not 1:
                num_match_count += 1
                writer.writerow({o_mmsi_field: mmsi})
    vprint(" - Done")
    vprint("Found %s non-matching records" % num_match_count)

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
