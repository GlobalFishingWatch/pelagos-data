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
Subcommand: getconfig
"""


from __future__ import unicode_literals

import inspect
from os.path import *
import shutil

from ... import assets
from ..components import *
from ...controller import *


#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#

__all__ = ['print_usage', 'print_help', 'print_long_usage', 'main']
SUBCOMMAND_NAME = basename(inspect.getfile(inspect.currentframe())).replace('subcommand_', '')


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """

    global SUBCOMMAND_NAME

    # TODO: Populate help
    vprint("""

    """.format(SUBCOMMAND_NAME, '-' * len(SUBCOMMAND_NAME), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(subcommand_name, configfile, args):

    """
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    if len(args) is 0:
        return print_help()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    overwrite_mode = False

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
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info',
                       '-h', '--h', '--usage', '-usage', '--help', '-help', 'help'):
                return print_help()

            # I/O settings
            elif arg in ('-overwrite', '--overwrite'):
                i += 1
                overwrite_mode = True

            # Positional arguments and errors
            else:
                i += 1
                arg_error = True
                vprint("ERROR: Unrecognized argument for subcommand %s: %s" % (subcommand_name, arg))

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

    # Check configfile
    if configfile is None:
        bail = True
        vprint("ERROR: Need a configfile")
    elif not overwrite_mode and isfile(configfile):
        bail = True
        vprint("ERROR: Overwrite=%s and configfile exists: %s" % (overwrite_mode, configfile))
    elif overwrite_mode and isfile(configfile) and not os.access(configfile, os.W_OK):
        bail = True
        vprint("ERROR: Overwrite=%s but need write access: %s" % configfile)
    elif not isfile(configfile) and not os.access(dirname(configfile), os.W_OK):
        bail = True
        vprint("ERROR: Need write access: %s" % dirname(configfile))

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Edit configfile
    #/* ----------------------------------------------------------------------- */#

    # Create a new configfile if needed
    if not isfile(configfile):
        try:
            shutil.copyfile(assets.sample_configfile, configfile)
            vprint("Copied to: %s" % configfile)
        except IOError as e:
            vprint(str(e))

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    return 0
