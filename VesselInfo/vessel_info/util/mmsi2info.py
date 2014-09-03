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


"""Given a CSV with a field containing an MMSI, give the same CSV back with several
additional fields:

vessel_name
vessel_class
vessel_callsign
vessel_imo
vessel_flag
"""


import csv
import os
from os.path import *
import sys

from .. import scrape
from .. import settings
import common


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_long_usage', 'print_help', 'print_license', 'print_help_info',
           'print_version', 'print_version', 'main']


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
Usage:
    {0} [options]
    """.format(UTIL_NAME, ' ' * len(UTIL_NAME)))

    return 1


#/* ======================================================================= */#
#/*     Define print_long_usage() function
#/* ======================================================================= */#

def print_long_usage():

    """
    Print all commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print_usage()
    print("""Options:
    -mfi --mmsi-field-name      Specify the field in the input csv
                                that contains the MMSI numbers
                                [default: mmsi]
    --overwrite                 Blindly overwrite the output file
    -r --retry                  Number of scrape retry attempts
                                [default: 3]
    -nh --no-human              Don't act like a human when scraping
                                Causes delay to be the pause value
    -p --pause                  Explicitly set the delay between
                                scrape attempts
                                [default: 0.5]
    -ua --user-agent            Specify the user agent for the request
                                [default: Mozilla/30.0]
    -onull --ocsv-null          Set the null value for the output CSV
                                [default: '']
    -s --subsample              Only process part of the input file

Scrapers:
    --no-marine-traffic         Don't scrape MarineTraffic.com
    --marine-traffic-url        Set the Marine Traffic base URL
                                [default: http://www.marinetraffic.com/en/ais/details/ships/]
    """.format(UTIL_NAME, ' ' * len(UTIL_NAME)))

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Print more detailed help information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print('''
Help: {0}
------{1}
This utility takes an input CSV containing a field of MMSi numbers and attempts
to find various pieces of information about the vessel.  The input CSV can
contain any number of fields and the MMSI field can be explicitly defined with
the '-mfi' flag.  All input fields are preserved but they are re-ordered
alphabetically and all values are qualified in the output file.

In order to retrieve information, the utility takes an MMSI, pauses for a few
seconds to act more like a human, and scrapes a website until it gets information
or until it exhausts the allotted number of retries.  If the scrape retrieved
information from the very first website, it skips the rest adds the information
to the output CSV.  If all retries were exhausted for the first website, it
attempts to scrape the second, and so on.  The following websites are scraped
in this order:

  1. MarineTraffic.com

The pause between scrape attempts can be done in two ways.  By default the utility
waits somewhere between 0.1 and 3 seconds between scrape attempts but an explicit
pause value can be set with the '--pause' option.  This pause can also be completely
turned off with '--pause 0'.
    '''.format(UTIL_NAME, '-' * len(UTIL_NAME)))

    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print licensing information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print(settings.__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Help Flags:
    --help-info     This printout
    --help          More detailed description of this utility
    --usage         Arguments, parameters, etc.
    --long-usage    Usage plus brief description of all options
    --version       Version and ownership information
    --short-version Only the version number
    --license       License information
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_short_version():

    """
    Only print the module version

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print(settings.__version__)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_version():

    """
    Print the module version and release date

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
%s v%s - released %s
    """ % (UTIL_NAME, settings.__version__, settings.__release__))

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
    Commandline logic

    :param args: arguments gathered from the commandline (sys.argv[1:])
    :type args: list

    :return: returns 0 on success and 1 on error
    :rtype: int
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    stream = sys.stdout
    input_csv_mmsi_field = 'mmsi'
    output_field_prefix = 'v_'
    overwrite_mode = False
    process_subsample = False

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    input_csv_file = None
    output_csv_file = None

    scraper_options = {}

    # Collected from commandline as ['key=value'] pairs but converted to a dictionary during the configuration
    # validation step.  Options are validated to make sure all required components are present but no checks
    # are made to ensure that the options are actual real options
    cmdl_auto_scrape_options = []
    cmdl_scraper_options = []
    auto_scrape_options = {}
    scraper_options = {}

    # auto_scrape_options = {
    #   'opt1': 'val1',
    #   'opt2': 'val2'
    # {

    # scrape_options = {
    #   'scraper1': {
    #       'opt1': 'val1',
    #       'opt2': 'val2'
    #   },
    #   'scraper1': {
    #       'opt1': 'val1',
    #       'opt2': 'val2'
    #   }
    # }

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse Arguments
    #/* ----------------------------------------------------------------------- */#

    i = 0
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
            elif arg in ('--long-usage', '-long-usage', '-lu'):
                return print_long_usage()

            # Scraper options
            elif arg == '-ao':
                i += 2
                cmdl_auto_scrape_options.append(args[i - 1])
            elif arg == '-so':
                i += 2
                cmdl_scraper_options.append(args[i - 1])

            # I/O options
            elif arg == '--overwrite':
                i += 1
                overwrite_mode = True
            elif arg in ('-imf', '--icsv-mmsi-field'):
                i += 2
                input_csv_mmsi_field = args[i - 1]
            elif arg in ('-ofp', '--ocsv-field-prefix'):
                i += 2
                output_field_prefix = args[i - 1]
            elif '--subsample=' in arg:
                i += 1
                process_subsample = common.string2type(arg.split('=', 1)[1])

            # Positional arguments and errors
            else:

                i += 1

                # Catch input CSV
                if input_csv_file is None:
                    input_csv_file = expanduser(arg)

                # Catch output CSV
                elif output_csv_file is None:
                    output_csv_file = expanduser(arg)

                # Catch unrecognized arguments
                else:
                    arg_error = True
                    stream.write("ERROR: Unrecognized argument: %s\n" % arg)

        # An argument with parameters likely didn't iterate 'i' properly
        except IndexError:
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters - current arg: %s\n" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate configuration / transform arguments
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        stream.write("ERROR: Did not successfully parse arguments\n")

    # Check input CSV
    if input_csv_file is None:
        bail = True
        stream.write("ERROR: Need an input CSV\n")
    elif not os.access(input_csv_file, os.R_OK):
        bail = True
        stream.write("ERROR: Can't access input CSV: %s\n" % input_csv_file)

    # Check output CSV
    if output_csv_file is None:
        bail = True
        stream.write("ERROR: Need an output CSV\n")
    elif not overwrite_mode and isfile(output_csv_file):
        bail = True
        stream.write("ERROR: Overwrite=%s and output file exists: %s\n" % (overwrite_mode, output_csv_file))
    elif overwrite_mode and isfile(output_csv_file) and not os.access(output_csv_file, os.W_OK):
        bail = True
        stream.write("ERROR: Overwrite=%s but can't access output file: %s\n" % output_csv_file)
    elif not isfile(output_csv_file):
        dname = dirname(output_csv_file)
        if dname == '':
            dname = './'
        if not os.access(dname, os.W_OK):
            bail = True
            stream.write("ERROR: Need write access for output file: %s\n" % output_csv_file)

    # Check auto-scrape options
    for aso in cmdl_auto_scrape_options:
        try:
            option, value = aso.split('=')
            value = common.string2type(value)

            # Add to options
            auto_scrape_options[option] = value
        except ValueError:
            bail = True
            stream.write("ERROR: Invalid auto-scrape option: %s\n" % aso)
    
    # Check individual scraper options
    for so in cmdl_scraper_options:
        try:
            s_name, key_vals = so.split(':')
            for kv in key_vals.split(','):
                option, value = kv.split('=')
                value = common.string2type(value)
                if s_name not in scraper_options:
                    scraper_options[s_name] = {option: value}
                else:
                    s_options = scraper_options[s_name]
                    s_options[option] = value
                    scraper_options[s_name] = s_options
        except ValueError:
            bail = True
            stream.write("ERROR: Invalid scraper option: %s\n" % so)

    # Check subsample
    if process_subsample is not None and not isinstance(process_subsample, int) or process_subsample < 1:
        bail = True
        stream.write("ERROR: Invalid subsample - must be an int >= 1: %s\n" % process_subsample)
        
    # Exit if an error was encountered
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prepare input and output file
    #/* ----------------------------------------------------------------------- */#

    num_rows = 0
    if process_subsample is not None:
        num_rows = process_subsample
    else:
        with open(input_csv_file, 'r') as i_f:
            reader = csv.DictReader(i_f)

            # Make sure the MMSI field is in the input file
            if input_csv_mmsi_field not in reader.fieldnames:
                stream.write("ERROR: MMSI field not found in input CSV field names: %s\n")
                stream.write("       Fields: %s\n" % ', '.join(reader.fieldnames))
                return 1

            # Figure out how many rows are in the input file
            for row in csv.DictReader(i_f):
                num_rows += 1

    # Prep I/O
    stream.write("Preparing input CSV: %s\n" % input_csv_file)
    with open(input_csv_file, 'r') as i_f:
        reader = csv.DictReader(i_f)
        stream.write("Preparing output CSV: %s\n" % input_csv_file)
        with open(output_csv_file, 'w') as o_f:
            ofields = [output_field_prefix + i for i in scrape.MMSI.ofields]
            writer = csv.DictWriter(o_f, fieldnames=reader.fieldnames + ofields)
            writer.writeheader()

            # Get a subsample if necessary
            if process_subsample is not None:
                reader = [row for i, row in enumerate(reader) if i <= process_subsample]
            
            # Add some formatting to the auto-scraper output
            auto_scrape_options['stream'] = stream
            auto_scrape_options['stream_prefix'] = '    '
            auto_scrape_options['scraper_options'] = scraper_options.copy()
            stream.write("Silently processing %s MMSI's unless an error is encountered...\n" % num_rows)
            for row in reader:

                result = scrape.auto_scrape(scrape.MMSI(row[input_csv_mmsi_field]), **auto_scrape_options)
                if result is not None:

                    # Add output field prefix to the result, combine with the input row, and write to output file
                    output_row = row.copy()
                    for key, value in result.iteritems():
                        key = output_field_prefix + key
                        output_row[key] = value
                else:
                    output_row = row.copy()

                writer.writerow(output_row)

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup
    #/* ----------------------------------------------------------------------- */#

    # Success
    stream.write("Done.\n")
    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Remove script name and give the rest to main
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))

    # Didn't get enough arguments - print usage
    else:
        sys.exit(print_usage())
