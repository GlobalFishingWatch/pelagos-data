#!/usr/bin/env python


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


"""
Discontinuity detector
"""


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import csv
from datetime import datetime
import json
import os
from os.path import abspath, expanduser, isfile, dirname
import sys

try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr
ogr.UseExceptions()
osr.UseExceptions()


#/* ======================================================================= */#
#/*     Global variables
#/* ======================================================================= */#

UTIL_NAME = 'disco-detect.py'


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage information


    Returns:

        1 for exit code purposes
    """

    global UTIL_NAME

    # TODO: Populate usage
    print("""
{0} [-q] [-tt seconds] [-dt distance] [-s schema] [-wm w|a]
{1} [-op csv|csv-no-schema|newline|frequency] [-sl num_lines]
{1} [-overwrite] [-a-srs srs_def] infile outfile
""".format(UTIL_NAME, " " * len(UTIL_NAME)))
    return 1


#/* ======================================================================= */#
#/*     Define print_long_usage() function
#/* ======================================================================= */#

def print_long_usage():

    """
    Print full commandline usage information


    Returns:

        1 for exit code purposes
    """

    global UTIL_NAME

    print_usage()
    print("""Options:
    infile -                    Input file for processing or '-' for stdin
    outfile -                   Output file for writing or '-' for stdout
    -q -quiet                   Suppress user output
    -th -time-threshold         Number of seconds allowed between points before
                                they are flagged as potentially discontinuous
                                [default: 259200]
    -dh -distance-threshold     Number of georeferenced distance units allowed
                                between points before they are flagged as
                                discontinuous.  Default assumes input is in degrees.
                                [default: 1]
    -s -schema                  Header for input file if it is a CSV.  If none
                                is supplied, the first row is used as the schema.
                                if the input file is determined to be new-line
                                delimited JSON, this option is ignored.  Note
                                that there is no default and it will silently
                                use the first line, which could lead to errors.
    -sl -skip-lines             Skip N lines in the input file
    -overwrite                  Overwrite the output file if it exists
    -wm -write-mode             Python supported write mode for writing the output
                                file.  Use -overwrite and -wm a to append to an
                                existing file.  If the output file exists it is
                                only overwritten if the -overwrite argument is
                                supplied, even though the default looks like it
                                might always be overwritten.
                                [default: w]
    -a-srs -assign-srs          Spatial reference to use for all input points
                                [default: EPSG:4326]
    -op -output-product         Specify the output product.  Valid options:
                                    csv = Any offending input rows as they were
                                        read from the input file.  The schema is
                                        added as the first row
                                    csv-no-schema = Same as input but without
                                        the schema row
                                    newline = same as csv but as newline JSON
                                    frequency = CSV containing MMSI's exhibiting
                                        discontinuity and the total number of
                                        offending points
                                    flag-* = Write all input rows but flag those
                                        exhibiting discontinuity.  New output
                                        field is {0}
                                    flag-csv = Flag output is CSV
                                    flag-csv-no-schema = Flag output is CSV
                                        without schema
                                    flag-newline = Flag output is newline delimited JSON
    """.format(UTIL_NAME))

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Detailed help information


    Returns:

        1 for exit code purposes
    """

    global UTIL_NAME

    # TODO: Populate help
    print("""
Help: {0}
------{1}
{2}""".format(UTIL_NAME, '-' * len(UTIL_NAME), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define NewlineJSONReader() class
#/* ======================================================================= */#

class NewlineJSONReader(object):

    """
    Allow newline delimited JSON to be read similarly to csv.DictReader
    """

    def __init__(self, f, fieldnames=None, delimiter=os.linesep):
        self.f = f
        self.delimiter = delimiter
        self.fieldnames = fieldnames
        if self.fieldnames is None:
            self.fieldnames = json.loads(self.f.readline().replace(self.delimiter, '')).keys()
            self.f.seek(0)

    def __iter__(self):
        return self

    def next(self):
        return json.loads(self.f.readline().replace(self.delimiter, ''))

    def seek(self, val):
        return self.f.seek(val)

    def close(self):
        self.f.close()


#/* ======================================================================= */#
#/*     Define NewlineJSONWriter() class
#/* ======================================================================= */#

class NewlineJSONWriter(object):

    """
    Allow newline delimited JSON to be written similarly to csv.DictWriter
    """

    def __init__(self, f, fieldnames=None, delimiter=os.linesep):
        self.f = f
        self.delimiter = delimiter
        self.fieldnames = fieldnames

    def writerow(self, row):
        if self.fieldnames:
            row = {k: v for k, v in row.iteritems() if k in self.fieldnames}
        self.f.write(json.dumps(row) + os.linesep)

    def write(self, row):
        self.writerow(row)

    def close(self):
        self.f.close()


#/* ======================================================================= */#
#/*     Define is_discontinuous() function
#/* ======================================================================= */#

def is_discontinuous(row, last_row, a_srs=None, tt=None, dt=None):

    last_timestamp = datetime.fromtimestamp(int(last_row['timestamp']))
    process_timestamp = datetime.fromtimestamp(int(row['timestamp']))
    td = process_timestamp - last_timestamp

    if not td.seconds <= tt:
        return False
    else:
        last_point = ogr.CreateGeometryFromWkt('POINT (%s %s)' % (last_row['longitude'], last_row['latitude']))
        last_point.AssignSpatialReference(a_srs)
        process_point = ogr.CreateGeometryFromWkt('POINT (%s %s)' % (row['longitude'], row['latitude']))
        process_point.AssignSpatialReference(a_srs)

        # Check distance
        return last_point.Distance(process_point) >= dt


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
In order to detect discontinuity, two lines are loaded.  If the timestamp differs
by more than the threshold set by -time-threshold, then the distance between
points is calculated.  If the distance is greater than the threshold set by
-distance-threshold then the points are assumed to be discontinuous.
 
Currently the output file is just a count of MMSI's and number of discontinuous points
    """

    global UTIL_NAME

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    if len(args) is 0:
        return print_usage()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    write_mode = 'w'
    skip_lines = 0
    overwrite_mode = False
    assign_srs_from_cmdl = 'EPSG:4326'
    time_threshold = 269200
    distance_threshold = 1
    quiet_mode = False
    output_product = 'csv'
    input_file_format = None

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    input_file = None
    output_file = None
    input_schema = None
    valid_output_products = ('frequency', 'csv', 'csv-no-schema', 'newline', 'flag-csv', 'flag-no-schema', 'flag-newline')
    valid_input_file_formats = ('csv', 'newline', 'json')

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse arguments
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
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--long-usage', '-long-usage', '-lu'):
                return print_long_usage()

            # Algorithm settings
            elif arg in ('-tt', '-time-threshold'):
                i += 2
                time_threshold = int(args[i - 1])
            elif arg in ('-dt', '-distance-threshold'):
                i += 2
                distance_threshold = int(args[i - 1])

            # Define the output schema
            elif arg in ('-s', '-schema', '-header'):
                i += 2
                input_schema = args[i - 1].split(',')

            # Skip lines in input file
            elif arg in ('-sl', '-skip-lines'):
                i += 2
                skip_lines = int(args[i - 1])

            # Determine if reading from stdin
            elif arg == '-' and not input_file and sys.stdin.isatty():
                i += 1
                arg_error = True
                print("ERROR: Trying to read from empty stdin")

            # Additional options
            elif arg in ('-q', '-quiet'):
                i += 1
                quiet_mode = True
            elif arg in ('-overwrite', '--overwrite'):
                i += 1
                overwrite_mode = True
            elif arg in ('-a-srs', '-assign-srs'):
                i += 2
                assign_srs_from_cmdl = args[i - 1]
            elif arg in ('-wm', '-write-mode'):
                i += 2
                write_mode = args[i - 1]
            elif arg in ('-op', '-output-product'):
                i += 2
                output_product = args[i - 1].lower()
            elif arg in ('-ff', '-file-format'):
                i += 2
                input_file_format = args[i - 1]
            elif arg == '-stdin':
                i += 1
                input_file = '-'
            elif arg == '-stdout':
                i += 1
                output_file = '-'

            # Catch invalid arguments
            elif arg[0] == '-' and arg != '-':
                i += 1
                arg_error = True
                print("ERROR: Unrecognized argument: %s" % arg)

            # Positional arguments and errors
            else:

                i += 1

                # Catch input file
                if input_file is None:
                    if arg == '-':
                        input_file = arg
                    else:
                        input_file = abspath(expanduser(arg))

                # Catch output file
                elif output_file is None:
                    if arg == '-':
                        output_file = arg
                    else:
                        output_file = abspath(expanduser(arg))

                # Unrecognized argument
                else:
                    arg_error = True
                    print("ERROR: Unrecognized argument: %s" % arg)

        # This catches several conditions:
        #   1. The last argument is a flag that requires parameters but the user did not supply the parameter
        #   2. The arg parser did not properly consume all parameters for an argument
        #   3. The arg parser did not properly iterate the 'i' variable
        #   4. An argument split on '=' doesn't have anything after '=' - e.g. '--output-file='
        except (IndexError, ValueError):
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters: %s" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Transform arguments
    #/* ----------------------------------------------------------------------- */#

    # Attempt to sniff file type
    if not input_file_format and input_file != '-':
        input_file_format = input_file.rsplit('.')[-1]

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate parameters
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Create SRS to apply to points
    try:
        assign_srs = osr.SpatialReference()
        assign_srs.SetFromUserInput(str(assign_srs_from_cmdl))
    except RuntimeError:
        assign_srs = None
        bail = True
        print("Invalid assign SRS: '%s'" % assign_srs_from_cmdl)

    # Check algorithm options
    if not 0 <= time_threshold:
        bail = True
        print("ERROR: Invalid time threshold - must be >= 0: '%s'" % time_threshold)
    if not 0 <= distance_threshold:
        bail = True
        print("ERROR: Invalid distance threshold - must be >= 0: '%s'" % distance_threshold)

    # Check output product options
    if output_product not in valid_output_products:
        bail = True
        print("ERROR: Invalid output product: '%s'" % output_product)
        print("       Options: %s" % ', '.join(valid_output_products))
    
    # Check input file format
    if input_file_format not in valid_input_file_formats:
        bail = True
        print("ERROR: Invalid input file format: '%s'" % input_file_format)
        print("       Options: %s" % ', '.join(valid_input_file_formats))
        
    # Check input files
    if input_file is None:
        bail = True
        print("ERROR: Need an input file")
    elif input_file != '-' and not os.access(input_file, os.R_OK):
        bail = True
        print("ERROR: Can't access input file: '%s'" % input_file)

    # Check output file
    if output_file is None:
        bail = True
        print("ERROR: Need an output file")
    elif output_file != '-' and not overwrite_mode and isfile(output_file):
        bail = True
        print("ERROR: Overwrite=%s but output file exists: '%s'" % (overwrite_mode, output_file))
    elif output_file != '-' and isfile(output_file) and not os.access(output_file, os.W_OK):
        bail = True
        print("ERROR: Need write access for output file: '%s'" % output_file)
    elif output_file != '-' and not isfile(output_file) and not os.access(dirname(output_file), os.W_OK):
        bail = True
        print("ERROR: Need write access for output dir: '%s'" % dirname(output_file))

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prepare data
    #/* ----------------------------------------------------------------------- */#

    # Be absolutely sure quiet mode is on if the output is stdout, otherwise the output will contain user feedback
    if output_file == '-':
        quiet_mode = True

    if not quiet_mode:
        print("Input file:  %s" % input_file)
        print("Output file: %s" % output_file)
        print("Schema: %s" % ','.join(input_schema) if isinstance(input_schema, (list, tuple)) else input_schema)

    # Get line count, which is only used when writing to a file and NOT for stdout
    prog_total = 0
    if not quiet_mode and output_file != '-':
        with sys.stdin if input_file == '-' else open(input_file) as i_f:
            for row in i_f:
                prog_total += 1

        # Remove the number of skipped lines and CSV header
        prog_total -= skip_lines
        if input_schema is None:
            prog_total -= 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Process data
    #/* ----------------------------------------------------------------------- */#

    flag_field = UTIL_NAME
    flag_val = 1

    # Open input file or stdin
    with sys.stdin if input_file == '-' else open(input_file) as i_f:

        # Open output file or stdin
        with sys.stdout if output_file == '-' else open(output_file, write_mode) as o_f:

            # Construct a reader
            if input_file_format == 'json':
                try:
                    reader = NewlineJSONReader(i_f)
                    fieldnames = reader.fieldnames
                except ValueError:
                    print("ERROR: Input file format is '%s' but could not be decoded" % input_file_format)
                    return 1
            elif input_file_format == 'csv':
                if input_schema:
                    reader = csv.DictReader(i_f, fieldnames=input_schema)
                else:
                    reader = csv.DictReader(i_f)
                fieldnames = reader.fieldnames
            else:
                raise IOError("Could not determine input file format - valid formats are newline delimited JSON and CSV")

            # Make sure the writer has the flag field if necessary
            if 'flag' in output_product:
                writer_fieldnames = reader.fieldnames + [flag_field]
            else:
                writer_fieldnames = reader.fieldnames

            # Construct a writer for the output product
            if output_product == 'frequency':
                # The 'frequency' writer is established later once all data is collected
                pass
            elif 'csv' in output_product:
                writer = csv.DictWriter(o_f, writer_fieldnames)
                if output_product in ('csv', 'flag-csv'):
                    writer.writeheader()
            elif 'newline' in output_product:
                writer = NewlineJSONWriter(o_f, writer_fieldnames)
            else:
                raise IOError("Invalid output product: '%s'" % output_product)

            # Loop over input file
            discontinuity_counts = {}
            last_row = None
            for prog_i, row in enumerate(reader):

                # Only process rows once the proper number of lines has been skipped
                if prog_i >= skip_lines:

                    # Update user, but NOT if writing to stdout
                    if not quiet_mode and output_file != '-':
                        sys.stdout.write("\r\x1b[K" + "    %s/%s" % (prog_i, prog_total))
                        sys.stdout.flush()

                    # Compare MMSI values - if they don't match then re-set the last row to start processing the new MMSI
                    try:
                        if last_row and row['mmsi'] != last_row['mmsi']:
                            last_row = None
                    except KeyError:
                        print(row)
                        print(last_row)
                        return 1

                    # If flagging output, make sure all rows contain the field
                    if 'flag' in output_product:
                        row[flag_field] = ''

                    # Normal processing
                    if last_row is not None and is_discontinuous(row, last_row, tt=time_threshold,
                                                                 dt=distance_threshold, a_srs=assign_srs):

                        # Flag output
                        if 'flag' in output_product:
                            row[flag_field] = flag_val

                        # Collect frequency counts
                        if output_product == 'frequency':
                            if row['mmsi'] not in discontinuity_counts:
                                discontinuity_counts[row['mmsi']] = 1
                            else:
                                discontinuity_counts[row['mmsi']] += 1

                        # Write discontinous row
                        else:
                            writer.writerow(row)

                    # Make sure all rows are written when flagging output
                    # This also catches MMSi's containing only a single point AND the firs row of every MMSI
                    elif 'flag' in output_product:
                        writer.writerow(row)

                    # Mark the row just processed as the last row in preparation for processing the next row
                    last_row = row.copy()

            #/* ----------------------------------------------------------------------- */#
            #/*     Dump results if output product is 'frequency'
            #/* ----------------------------------------------------------------------- */#

            if output_product == 'frequency':
                writer = csv.DictWriter(o_f, ['mmsi', 'count'])
                writer.writeheader()
                for mmsi, count in discontinuity_counts.iteritems():
                    writer.writerow({'mmsi': mmsi, 'count': count})

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    if not quiet_mode:
        print(" - Done")
    return 0


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Didn't get enough arguments - print usage and exit
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - give sys.argv[1:] to main()
    else:
        sys.exit(main(sys.argv[1:]))
