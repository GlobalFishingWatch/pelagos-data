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
import inspect
import os
from os.path import *
import sys

from .. import scrape
from .. import settings
import common


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__docname__ = basename(inspect.getfile(inspect.currentframe()))
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
{0} [--help-info] [-ss N] [--overwrite] [-im field_name]
{1} [-ao option=value,o=v,...] [-so name:option=value,o=v,...]
{1} [-op ofield_prefix] input_csv output_csv
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
    --help          More detailed description of this utility
    --help-info     This printout
    --license       License information
    --long-usage    Usage plus brief description of all options
    --short-version Only the version number
    --version       Version and ownership information
    --usage         Arguments, parameters, etc.
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
%s v%s released %s
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
                process_subsample = common.string2type(args[i - 1].split('=', 1)[1])

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
                value = common.string2type(value)
                if value not in scrape.auto_scrape(None, _get_options=True).keys():
                    bail = True
                    stream.write("ERROR: Unrecognized auto-scrape option: %s" % kv)
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
                value = common.string2type(value)
                if option not in scrape.MMSI.scraper_options.keys():
                    bail = True
                    stream.write("ERROR: Invalid option for scraper '%s': %s" % (s_name, kv))
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
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))

    # Didn't get enough arguments - print usage
    else:
        sys.exit(print_usage())
