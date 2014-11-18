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
Pipeline controller
"""


from __future__ import unicode_literals

from os.path import abspath, expanduser

from .. import components
from ..components import *
from ...controller import *
from ... import settings

from . import subcommand_check
from . import subcommand_copyoutput
from . import subcommand_get
from . import subcommand_getconfig
from . import subcommand_validate


#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#

# TODO: Fix __all__ - when uncommented a "TypeError: Item in ``from list'' not a string" is thrown
#__all__ = ['print_usage', 'print_help', 'print_long_usage', 'main'] + [unicode(_i) for _i in locals().keys() if 'subcommand_' in _i]
UTIL_NAME = 'pp-controller.py'


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
{0} [--help-info]

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
    """)

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
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    if len(args) is 0:
        return print_usage()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    configfile = settings.CONFIGFILE

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    subcommand_name = None
    subcommand_args = []

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
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--license', '-usage'):
                return print_license()

            # User feedback
            elif arg in ('-q', '-quiet'):
                i += 1
                components.VERBOSE_MODE = False

            # Set configfile globally
            elif arg in ('-c', '-config', '--config'):
                i += 2
                configfile = abspath(expanduser(args[i - 1]))

            # Positional arguments and errors
            else:

                i += 1

                # Catch sub-command
                if subcommand_name is None:
                    subcommand_name = arg

                # Collect all other arguments to be passed to the sub-command
                else:
                    subcommand_args.append(arg)

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

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        vprint("ERROR: Did not successfully parse arguments")

    # Check sub-command
    if subcommand_name is None:
        bail = True
        vprint("ERROR: Need a sub-command")

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Call sub-command and exit
    #/* ----------------------------------------------------------------------- */#

    # Make sure configfile is actually valid
    if not config.is_clean(configfile):
        vprint("ERROR: Problem parsing configfile")
        return 1

    # Call the subcommand
    sc = 'subcommand_%s' % subcommand_name
    if sc in globals():
        return globals()[sc].main(subcommand_name, configfile, subcommand_args)
    else:
        vprint("ERROR: Invalid sub-command: %s" % subcommand_name)
        return 1


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
