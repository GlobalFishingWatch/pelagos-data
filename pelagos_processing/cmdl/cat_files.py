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
Concatenate files
"""


from __future__ import unicode_literals

from glob import glob
from os.path import abspath, expanduser, isfile, dirname

from . import components
from .components import *
from ..controller import *
from .. import raw


#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#

__all__ = ['print_usage', 'print_help', 'print_long_usage', 'main']
UTIL_NAME = 'catfiles.py'


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Command line usage information

    :return: 1 for exit code purposes
    :rtype: int
    """

    global UTIL_NAME

    # TODO: Populate usage
    vprint("""
{0} [--help-info] [-q] [-s schema] [-m write_mode] ofile ifile [ifile ...]

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

    print_usage()
    vprint("""Options:
    -q -quiet           Suppress all output
    -m -mode            Write mode for updating file: 'w' for overwrite, or 'a'
                        for append
                        [default: w]
    -s -schema          Output file header as: field1,field2,...
                        To skip writing a schema, use an empty string
                        [default: {0}]
    ofile               Target file
    ifile               Input file to be concatenated.  See --help for information
                        about getting around the command line's argument limit when
                        attempting to process a large number of files.  Using '-'
                        as an input file causes

    """.format(','.join(raw.RAW_SCHEMA)))

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """

    global UTIL_NAME

    # TODO: Populate help
    vprint("""
Help: {0}
------{1}
{2}
    """.format(UTIL_NAME, '-' * len(UTIL_NAME), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
Concatenate multiple files into a single target file.  Target file can be
overwritten or updated according to the write mode supplied via -mode, which
directly sets the mode in Python's open() function.

If a command line error stating the argument list is too long is encountered
switch to using quoted wildcard paths, which lets Python handle the argument
expansion.
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    if len(args) is 0:
        return print_usage()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    output_schema = raw.RAW_SCHEMA
    write_mode = 'w'

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    input_files = []
    output_file = None

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
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info', '-h', '--h'):
                return print_help_info()
            elif arg in ('--help', '-help'):
                return print_help()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--long-usage', '-long-usage'):
                return print_long_usage()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--short-version', '-short-version'):
                return print_short_version()
            elif arg in ('--license', '-license'):
                return print_license()

            # User feedback
            elif arg in ('-q', '-quiet'):
                i += 1
                components.VERBOSE_MODE = False

            # Define the output schema
            elif arg in ('-s', '-schema', '-header'):
                i += 2
                output_schema = args[i - 1]

            # Additional options
            elif arg in ('-m', '-mode'):
                i += 2
                write_mode = args[i - 1]

            # Catch invalid arguments
            elif arg[0] == '-' and arg != '-':
                i += 1
                arg_error = True
                vprint("ERROR: Unrecognized argument: %s" % arg)

            # If reading from empty stdin, throw an error
            elif arg == '-' and sys.stdin.isatty():
                i += 1
                arg_error = True
                vprint("ERROR: Trying to read from empty stdin")

            # Positional arguments and errors
            else:

                i += 1

                # Catch output file
                if output_file is None:
                    output_file = abspath(expanduser(arg))

                else:

                    expanded_arg = abspath(expanduser(arg))

                    # Read from stdin
                    if arg == '-' and not sys.stdin.isatty():
                        f_list = sys.stdin

                    # Let python handle glob expansion
                    elif '*' in arg:
                        f_list = glob(expanded_arg)

                    # Argument is just a file path - wrap in a list to make iterable
                    else:
                        f_list = [expanded_arg]

                    # Loop through all records, normalize the path, and append to input files
                    for record in f_list:
                        r = abspath(expanduser(record))
                        if r not in input_files:
                            input_files.append(r)

        # This catches several conditions:
        #   1. The last argument is a flag that requires parameters but the user did not supply the parameter
        #   2. The arg parser did not properly consume all parameters for an argument
        #   3. The arg parser did not properly iterate the 'i' variable
        #   4. An argument split on '=' doesn't have anything after '=' - e.g. '--output-file='
        except (IndexError, ValueError):
            i += 1
            arg_error = True
            vprint("ERROR: An argument has invalid parameters: %s" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate parameters
    #/* ----------------------------------------------------------------------- */#

    # Make sure the list of input files is unique
    input_files = list(set(input_files))

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        vprint("ERROR: Did not successfully parse arguments")

    # Check output file
    if output_file is None:
        bail = True
        vprint("ERROR: Need an output file")
    elif isfile(output_file) and not os.access(output_file, os.W_OK):
        bail = True
        vprint("ERROR: Need write access: %s" % output_file)
    elif not isfile(output_file) and not os.access(dirname(output_file), os.W_OK):
        bail = True
        vprint("ERROR: Need write access: %s" % dirname(output_file))

    # Check input files
    if len(input_files) is 0:
        bail = True
        vprint("ERROR: Need at least one input file")
    for ifile in input_files:
        if not os.access(ifile, os.R_OK):
            bail = True
            vprint("ERROR: Can't access input file: %s" % ifile)

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Process files
    #/* ----------------------------------------------------------------------- */#

    vprint("Output file: %s" % output_file)
    vprint("Write mode: %s" % write_mode)
    vprint("Schema: %s" % output_schema)
    vprint("Concatenating %s files ..." % len(input_files))

    try:
        if not raw.cat_files(input_files, output_file, schema=output_schema, write_mode=write_mode):
            vprint("ERROR: Did not successfully concatenate files")
            return 1
    except Exception as e:
        vprint(unicode(e))
        return 1

    vprint("Done")
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
