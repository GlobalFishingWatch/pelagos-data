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
Given a CSV with a field containing an MMSI, give the same CSV back with additional
vessel attributes:
    name
    class
    callsign
    imo
    flag
"""


import csv
import inspect
import os
from os.path import *
import sys

from .. import scrape
from common import *


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__docname__ = basename(inspect.getfile(inspect.currentframe()))
__all__ = ['print_usage', 'print_long_usage', 'print_help', 'main']


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
{0} [--help-info] [-ss N] [-op ofield_prefix] [-im field_name]
{1} [-ao option=value,o=v,...] [-so name:option=value,o=v,...]
{1} [--overwrite] input_csv output_csv
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
    -ao -auto-option    Options to be passed to the engine that drives the
                        scraping process
    -so -scraper-option Options to be passed to specific scrapers
    -mf -mmsi-field     Specify which field in the input_csv contains the
                        MMSI values
                        [default: mmsi]
    -op -output-prefix  Vessel information collected by the scrapers is appended
                        to the input_csv so in order to prevent any fields from
                        being overwritten a prefix for the new output fields can
                        be specified
                        [default: v_]
    -ss -subsample      Only process N rows of the input file
    --overwrite         Blindly overwrite the output file if it exists
    """.format(UTIL_NAME, ' ' * len(UTIL_NAME)))

    # Print the scraper order
    print("Default Scraper Order:")
    for i, sname in enumerate(scrape.MMSI.scraper_order):
        print("    %s. %s" % (i + 1, sname))
    print("")

    # Add auto options
    print("Auto Options:")
    auto_options = scrape.auto_scrape(None, _get_options=True)
    a_keys = auto_options.keys()
    a_keys.sort()
    max_opt = max([len(i) for i in a_keys])
    for opt in a_keys:
        pad = ' ' * (max_opt - len(opt))
        print("    %s%s %s" % (opt, pad, auto_options[opt]))
    print("")

    # Add scraper options
    print("Scraper Options:")
    scraper_options = scrape.MMSI.scraper_options
    scrapers = scraper_options.keys()
    scrapers.sort()
    for sname in scrapers:
        print("    %s" % sname)
        s_options = scraper_options[sname]
        s_keys = s_options.keys()
        s_keys.sort()
        max_opt = max([len(i) for i in s_keys])
        for opt in s_keys:
            pad = ' ' * (max_opt - len(opt))
            print("        %s%s %s" % (opt, pad, s_options[opt]))
        print("")

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

    print("""
Help: {0}
------{1}""".format(UTIL_NAME, '-' * len(UTIL_NAME)))
    print(main.__doc__)

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
Given a CSV file with a field containing MMSI values, automatically scrape all
supported websites for additional vessel information.  An attempt to scrape each
website is made 3 times by default unless a successful scrape happens before
then.  A pause between scrape attempts occurs in order to prevent overloading
the sites being scraped.  By default this value is 3 seconds but can be specified
if needed.

If a successful scrape does not occur and multiple scrapers are to be used,
then the next scraper in the list attempts to retrieve information.  Null values
are written if all scrapers fail for a given MMSI.  Additional fields present in
the input CSV are preserved in the output CSV.  A test is performed to ensure
that none of these fields will be overwritten, but if this test fails the user
can add a prefix to the output fields with the '-output-prefix' flag.  For
example, if the input CSV already has a 'callsign' field the user can specify
create a unique name with '-output-prefix vessel_'

By default a 'v_' is prepended to the additional output fields.  This can be
turned off with '--output-prefix ""'

The number of retries and which scrapers to use can be specified via the
'-auto-option' flag.  For more information about the scraper order and options
see the usage information.


Exit codes:
    0 on success
    1 on failure


Sample Commands
---------------

All scrapers with default settings:

    $ mmsi2info.py \\
        Input_MMSI.csv \\
        Output.csv


All scrapers but specify a different output field prefix and input MMSI field:

    $ mmsi2info.py \\
        -mf Vessel_MMSI \\
        -op vessel_ \\
        Input_MMSI.csv \\
        Output.csv


All scrapers but specify a different number of retries, scraper order, and pause:

    $ mmsi2info.py \\
        -mf Vessel_MMSI \\
        -op vessel_ \\
        -ao retry=10 \\
        -ao scraper_order=fleetmon,marine_traffic,vessel_finder \\
        -ao pause=1
        Input_MMSI.csv \\
        Output.csv


Same as above but only use FleetMON:
    $ mmsi2info.py \\
        -mf Vessel_MMSI \\
        -op vessel_ \\
        -ao retry=10,scraper_order=fleetmon,pause=1 \\
        Input_MMSI.csv \\
        Output.csv


All scrapers but give FleetMON a timeout value and the required API user and key:
    $ mmsi2info.py \\
        -so fleetmon:api_user=fm_user,api_key=fm_key,timeout=100 \\
        Input_MMSI.csv \\
        Output.csv
    """

    # Check arguments
    if len(args) is 0:
        return print_usage()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    stream = sys.stdout
    input_csv_mmsi_field = 'mmsi'
    output_field_prefix = 'v_'
    overwrite_mode = False
    process_subsample = None
    print_progress = True

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    input_csv_file = None
    output_csv_file = None

    # Collected from commandline as ['key=value'] pairs but converted to a dictionary during the configuration
    # validation step.  Options are validated to make sure all required components are present but no checks
    # are made to ensure that the options are actual real options
    cmdl_auto_scrape_options = []
    cmdl_scraper_options = []
    auto_scrape_options = {}
    scraper_options = {}

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

            # Scraper options
            elif arg in ('-ao', '-auto-option'):
                i += 2
                cmdl_auto_scrape_options.append(args[i - 1])
            elif arg in ('-so', '-scraper-option'):
                i += 2
                cmdl_scraper_options.append(args[i - 1])

            # I/O options
            elif arg in ('-overwrite', '--overwrite'):
                i += 1
                overwrite_mode = True
            elif arg in ('-mf', '-mmsi-field'):
                i += 2
                input_csv_mmsi_field = args[i - 1]
            elif arg in ('-op', '-output-prefix'):
                i += 2
                output_field_prefix = args[i - 1]
            elif arg in ('-ss', '-subsample'):
                i += 2
                process_subsample = string2type(args[i - 1].split('=', 1)[1])

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
        except (IndexError, ValueError):
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

    # Check auto-scrape options.  Input is a lsit of strings meeting one of the following specifications
    # option1=val1
    # option1=val1,option2=val2
    #
    # Resulting dict:
    #   auto_scrape_options = {
    #      'opt1': 'val1',
    #      'opt2': 'val2'
    #   {
    for aso in cmdl_auto_scrape_options:
        try:
            for kv in aso.split(','):
                option, value = kv.split('=', 1)
                value = string2type(value)
                if option not in scrape.auto_scrape(None, _get_options=True).keys():
                    bail = True
                    stream.write("ERROR: Unrecognized auto-scrape option: %s\n" % kv)
                else:
                    auto_scrape_options[option] = value
        except ValueError:
            bail = True
            stream.write("ERROR: Auto-scrape option does not meet specification: %s\n" % aso)
            stream.write("       option1=val1,option2=val2\n")
    
    # Check individual scraper options.  Input is a list of strings meeting one of the following specifications:
    # scraper_name:option1=val1
    # scraper_name:option1=val1,option2=val2
    #
    # Resulting dict:
    #    scrape_options = {
    #      'scraper1': {
    #          'opt1': 'val1',
    #          'opt2': 'val2'
    #      },
    #      'scraper1': {
    #          'opt1': 'val1',
    #          'opt2': 'val2'
    #      }
    #    }
    for so in cmdl_scraper_options:
        try:
            s_name, key_vals = so.split(':')
            for kv in key_vals.split(','):
                option, value = kv.split('=')
                value = string2type(value)
                if option not in scrape.MMSI.scraper_options[s_name].keys():
                    bail = True
                    stream.write("ERROR: Invalid option for scraper '%s': %s\n" % (s_name, kv))
                # Valid option - add to scraper options
                else:
                    if s_name not in scraper_options:
                        scraper_options[s_name] = {option: value}
                    else:
                        s_options = scraper_options[s_name]
                        s_options[option] = value
                        scraper_options[s_name] = s_options
        except ValueError:
            bail = True
            stream.write("ERROR: Scraper option does not meet specification: %s\n" % so)
            stream.write("       scraper_name:option1=val1,option2=val2\n")

    # Check subsample
    if process_subsample is not None and not isinstance(process_subsample, int) or process_subsample is not None and process_subsample < 1:
        bail = True
        stream.write("ERROR: Invalid subsample - must be an int >= 1: %s\n" % process_subsample)
        
    # Exit if an error was encountered
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prepare input and output file
    #/* ----------------------------------------------------------------------- */#

    num_rows = 0
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
                reader = [row for i, row in enumerate(reader) if i <= process_subsample - 1]
                num_rows = len(reader)
            
            # Add some formatting to the auto-scraper output
            auto_scrape_options['stream'] = stream
            auto_scrape_options['stream_prefix'] = '    '
            auto_scrape_options['scraper_options'] = scraper_options.copy()
            # TODO: User feedback: stream.write("Silently processing %s MMSI's unless an error is encountered...\n" % num_rows)
            # TODO: User feedback: stream.write("Processing...\n" % num_rows)
            prog_i = 0
            for row in reader:

                # TODO: User feedback
                if print_progress:
                    prog_i += 1
                    stream.write("\r\x1b[K" + "    %s/%s - MMSI: %s" % (str(prog_i), str(num_rows), row[input_csv_mmsi_field]))
                    stream.flush()

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
    stream.write(" - Done\n")
    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Remove script name and give the rest to main
    sys.exit(main(sys.argv[1:]))
