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
Process raw delivered data
"""


import csv
import inspect
import logging
import os
from os.path import *
import sys

from components import *
from .. import raw
from .. import settings


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__all__ = ['print_usage', 'print_long_usage', 'print_help', 'main']
UTIL_NAME = 'process-ais.py'


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage information


    Returns:

        1 for exit code purposes
    """

    print("""
{0} [-help-info] [-q|-v] infile outfile
    """.format(UTIL_NAME, ' ' * len(UTIL_NAME)))

    return 1


#/* ======================================================================= */#
#/*     Define print_long_usage() function
#/* ======================================================================= */#

def print_long_usage():

    """
    Print all commandline usage information


    Returns:

        1 for exit code purposes
    """

    print_usage()
    print("""Options:
    -q -quiet       Be quiet
    -v -verbose     Yak yak yak
    infile          Input CSV or '-' for stdin
    outfile         Output CSV or '-' for stdout
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Print more detailed help information


    Returns:

        1 for exit code purposes
    """

    print("""
Help: {0}
------{1}""".format(UTIL_NAME, '-' * len(UTIL_NAME)))
    print(main.__doc__)

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    # Check arguments
    if len(args) is 0:
        return print_usage()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#
    
    log_level = logging.INFO
    overwrite_mode = False

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    infile = None
    outfile = None

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
            elif arg in ('-v', '-verbose', '--verbose'):
                i += 1
                log_level = logging.DEBUG
            elif arg in ('-q', '-quiet', '--quiet'):
                i += 1
                log_level = logging.ERROR

            # Additional options
            elif arg in ('-overwrite', '--overwrite'):
                i += 1
                overwrite_mode = True

            # Positional arguments and errors
            else:

                i += 1

                # Catch infile
                if infile is None:
                    infile = arg
                    if infile != '-':
                        infile = abspath(normpath(infile))

                # Catch outfile
                elif outfile is None:
                    outfile = arg
                    if outfile != '-':
                        outfile = abspath(normpath(outfile))

        # This catches several conditions:
        #   1. The last argument is a flag that requires parameters but the user did not supply the parameter
        #   2. The arg parser did not properly consume all parameters for an argument
        #   3. The arg parser did not properly iterate the 'i' variable
        #   4. An argument split on '=' doesn't have anything after '=' - e.g. '--output-file='
        except (IndexError, ValueError):
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters - current arg: %s" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate configuration / transform arguments
    #/* ----------------------------------------------------------------------- */#

    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        logging.error("Did not successfully parse arguments")

    # Check input file
    if infile is None:
        bail = True
        logging.error("Need an infile")
    elif not os.access(infile, os.R_OK):
        bail = True
        logging.error("Can't access input file: %s" % infile)

    # Check outfile
    if outfile is None:
        bail = True
        logging.error("Need an outfile")
    elif not overwrite_mode and isfile(outfile) and outfile != '-':
        bail = True
        logging.error("Overwrite=%s and output file exists: %s" % (overwrite_mode, outfile))
    elif overwrite_mode and isfile(outfile) and not os.access(outfile, os.W_OK):
        bail = True
        logging.error("Need write permission: %s" % outfile)
    elif not isfile(outfile) and not os.access(dirname(outfile), os.W_OK):
        bail = True
        logging.error("Need write permission: %s" % dirname(outfile))

    # Exit if an error was encountered
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Process data
    #/* ----------------------------------------------------------------------- */#



    with sys.stdin if infile == '-' else open(infile, 'rb') as csv_in:
        with sys.stdout if outfile == '-' else open(outfile, 'w') as csv_out:

            progress_total = len([i for i in csv_in.readlines()])
            csv_in.seek(0)

            progress_lookup = {int(progress_total * i / 100): i for i in range(0, 110, 10)}

            # TODO: Figure out how to programmatically get the output fields from somewhere

            reader = csv.DictReader(csv_in)
            fieldnames = reader.fieldnames

            fieldnames.extend(['gridcode', 'interval', 'type', 'next_gridcode'])
            writer = csv.DictWriter(csv_out, fieldnames, lineterminator=os.linesep)
            writer.writeheader()

            previous_row = None

            for idx, row in enumerate(reader):

                row_out = raw.transform_raw_row(row, prev_row=previous_row, log=settings.logging)
                if row_out:
                    writer.writerow(row_out)

                # Update user
                if idx in progress_lookup:
                    logging.info("Completed %s%%" % progress_lookup[idx])

            if previous_row:
                previous_row['type'] = settings.TYPE_SEGMENT_END
                writer.writerow(previous_row)

            # Include final stats in output
            logging.info(raw.TRANSFORM_RAW_ROW_STATS)
            logging.info("Done")


    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup
    #/* ----------------------------------------------------------------------- */#

    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Remove script name and give the rest to main
    sys.exit(main(sys.argv[1:]))
