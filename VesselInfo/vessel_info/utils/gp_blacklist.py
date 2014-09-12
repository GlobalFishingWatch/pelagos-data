
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
Scrape Greenpeace's vessel blacklist and output a CSV
"""


from __future__ import print_function
from __future__ import unicode_literals

import csv
import inspect
import os
from os.path import *
import sys

import common
from common import *
from .. import scrape


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__docname__ = basename(inspect.getfile(inspect.currentframe()))
__all__ = ['print_help', 'print_usage', 'print_long_usage', 'main']


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


    Returns:

        1 for exit code purposes
    """

    vprint("""
{0} [-help-info] [-q] [-so option=value,o=v]
{1} [-overwrite] output_csv
    """.format(UTIL_NAME, ' ' * len(UTIL_NAME)))

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

    print_usage()
    vprint("""Options:
    -q, -quiet              Suppress all progress and status reports
    -so, -scraper-option    Options to be passed to specific scrapers
    -overwrite              Blindly overwrite output file if it exists
    """)

    # Add scraper options
    print("Scraper Options:")
    scraper_options = scrape.gp_blacklist(get_scraper_options=True)
    s_keys = scraper_options.keys()
    s_keys.sort()
    max_opt = max([len(i) for i in scraper_options.keys()])
    for opt in s_keys:
        pad = ' ' * (max_opt - len(opt))
        vprint("    %s%s %s" % (opt, pad, scraper_options[opt]))
    vprint("")
    return 1


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_help():

    """
    Print commandline usage information

    Returns:

        1 for exit code purposes
    """

    vprint("""
Help: {0}
------{1}""".format(UTIL_NAME, '-' * len(UTIL_NAME)))
    vprint(main.__doc__)

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):
    
    """
Greenpeace maintains a list of vessels it has classified as blacklisted.  This
utility scrapes their registry and outputs a CSV with almost all of the values
in a machine-readable format.  A list of vessels and links to their pages can
be found here:

http://blacklist.greenpeace.org/1/vessel/list?gp_blacklist=1&startswith=A-Z

The URLs are extracted and then scraped individually to retrieve additional
vessel attributes.


Exit Codes:

    0 on success
    1 on failure


Sample Commands
---------------

Scrape the blacklist and save as a CSV

    $ gp_blacklist.py \\
        Greenpeace_Blacklist.csv


Same as above but wait 15 seconds max for a HTTP response

    $ gp_blacklist.py \\
        -so timeout=15 \\
        Greenpeace_Blacklist.csv
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

    overwrite_mode = False
    
    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#
    
    output_csv_file = None

    # Options collected from the commandline as 'option=val' are processed into a dictionary of {'key': 'val'} pars
    # during the validation step
    cmdl_scraper_options = []
    scraper_options = {}
    
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
                i += 1
                return print_help()
            elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo', '-h', '--h'):
                i += 1
                return print_help_info()
            elif arg in ('--license', '-license'):
                i += 1
                return print_license()
            elif arg in ('--version', '-version'):
                i += 1
                return print_version()
            elif arg in ('--short-version', '-short-version'):
                i += 1
                return print_short_version()
            elif arg in ('--usage', '-usage'):
                i += 1
                return print_usage()
            elif arg in ('--long-usage', '-long-usage'):
                i += 1
                return print_long_usage()
            
            # User feedback
            elif arg in ('-q', '-quiet'):
                i += 1
                common.VERBOSE_MODE = False

            # Configure scraper
            elif arg in ('-so', '-scraper-option'):
                i += 2
                cmdl_scraper_options.append(args[i - 1])

            # Additional options
            elif arg in ('-overwrite', '--overwrite'):
                i += 1
                overwrite_mode = True

            # Positional arguments and errors
            else:

                # Assume all other arguments are input files to be compared
                i += 1
                output_csv_file = normpath(expanduser(arg))

        # This catches several conditions:
        #   1. The last argument is a flag that requires parameters but the user did not supply the parameter
        #   2. The arg parser did not properly consume all parameters for an argument
        #   3. The arg parser did not properly iterate the 'i' variable
        #   4. An argument split on '=' doesn't have anything after '=' - e.g. '--output-file='
        except (IndexError, ValueError):
            i += 1
            arg_error = True
            vprint("ERROR: An argument has invalid parameters - current arg: %s" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate configuration / transform arguments
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        vprint("ERROR: Did not successfully parse arguments")

    # Check output files
    if output_csv_file is None:
        bail = True
        vprint("ERROR: Need an output file")
    elif not overwrite_mode and isfile(output_csv_file):
        bail = True
        vprint("ERROR: Overwrite=%s and output file exists: %s" % (overwrite_mode, output_csv_file))
    elif overwrite_mode and isfile(output_csv_file) and not os.access(output_csv_file, os.W_OK):
        bail = True
        vprint("ERROR: Need write permission: %s" % output_csv_file)
    else:
        _o_dir = dirname(output_csv_file)
        if _o_dir == '':
            _o_dir = normpath('./')
        if not os.access(_o_dir, os.W_OK):
            bail = True
            vprint("ERROR: Need write permission for output directory: %s" % _o_dir)

    # Check scraper options
    for so in cmdl_scraper_options:
        try:
            for kv in so.split(','):
                option, value = kv.split('=')
                value = string2type(value)
                if option not in scrape.gp_blacklist(get_scraper_options=True):
                    bail = True
                    vprint("ERROR: Unrecognized scraper option: %s" % kv)
                else:
                    scraper_options[option] = value
        except ValueError:
            bail = True
            vprint("ERROR: Scraper option does not meet specification 'option=value,o=v,...': %s" % so)

    # Found an error - exit
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Process data
    #/* ----------------------------------------------------------------------- */#

    with open(output_csv_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=scrape.gp_blacklist(get_output_fields=True))
        writer.writeheader()

        vprint("Getting list of vessels ...")
        vessel_list = scrape.gp_blacklist(return_urls=True, **scraper_options)

        progress_i = 0
        progress_max = len(vessel_list)
        vprint("Found %s vessels - processing ..." % progress_max)
        for vessel_url in vessel_list:

            # Update user
            progress_i += 1
            vprint("\r\x1b[K" + "    %s/%s" % (progress_i, progress_max), flush=True)

            # Get vessel information
            writer.writerow(scrape.gp_blacklist_vessel(vessel_url, **scraper_options))

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    vprint(" - Done")
    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Remove script name and give the rest to main
    sys.exit(main(sys.argv[1:]))
