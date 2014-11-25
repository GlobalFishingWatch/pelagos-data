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
Subcommand: copyoutput
"""


from __future__ import unicode_literals

import inspect
from os.path import *

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
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    target_dir = None
    nohup_output = 'nohup.out'

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
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info', '-h', '--h', '--usage', '-usage'):
                return print_help_info()

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
    elif not os.access(configfile, os.R_OK):
        bail = True
        vprint("ERROR: Can't access configfile: %s" % configfile)

    # Check if output directory exists
    if not Controller._exists(target_dir):
        bail = True
        vprint("ERROR: Can't find target directory: %s" % target_dir)

    # Check the nohup output file
    if not isfile(nohup_output):
        bail = True
        vprint("ERROR: Can't find nohup output: %s" % nohup_output)

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Execute copies
    #/* ----------------------------------------------------------------------- */#

    controller = Controller(configfile)
    encountered_error = False

    # Copy all of the process outputs
    for step in controller.steps:
        try:
            output_file = controller.get('run.%s_output' % step)
            if not isfile(output_file):
                vprint("ERROR: Could not find output file for '%s': %s" % (step, output_file))
            else:
                p = subprocess.Popen(['gsutil', 'cp', output_file, controller.run_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = p.communicate()
                if output and not err:
                    vprint("Copied %s to %s" % (output_file, controller.run_dir))
                elif not output and err:
                    vprint("ERROR: Tried to copy %s to %s: %s" % (output_file, controller.run_dir, err))
                    encountered_error = True
                else:
                    vprint(err)
                    encountered_error = True
        except KeyError:
            # Only copy stuff that actually has a defined output in the
            pass

    # Copy the nohup.out file
    p = subprocess.Popen(['gsutil', 'cp', nohup_output, controller.run_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    if output and not err:
        vprint("Copied %s to %s" % (nohup_output, controller.run_dir))
    elif not output and err:
        vprint("ERROR: Tried to copy %s to %s: %s" % (nohup_output, controller.run_dir, err))
        encountered_error = True
    else:
        vprint(err)
        encountered_error = True

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and exit
    #/* ----------------------------------------------------------------------- */#

    if encountered_error:
        return 1
    else:
        return 0
