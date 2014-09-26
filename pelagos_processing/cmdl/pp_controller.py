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
Clip arbitrary regions to quad tree levels
"""


import inspect
import os
from os.path import *
import shutil
import sys

from .. import assets
import components
from components import *
from .. import controller
from .. import settings


#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#

__all__ = ['print_usage', 'print_help', 'print_long_usage', 'main']
__docname__ = basename(inspect.getfile(inspect.currentframe()))


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Command line usage information

    :return: 1 for exit code purposes
    :rtype: int
    """
    # TODO: Populate usage
    vprint("""
{0} [--help-info]

""".format(__docname__, " " * len(__docname__)))
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
    # TODO: Populate help
    vprint("""
Help: {0}
------{1}
{2}
    """.format(__docname__, '-' * len(__docname__), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define print_sub_get_help() function
#/* ======================================================================= */#

def print_sub_validate_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """
    # TODO: Populate help
    vprint("""

    """.format(__docname__, '-' * len(__docname__), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define subcommand_validate() function
#/* ======================================================================= */#

def subcommand_validate(subcommand_name, args):

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    configfile = settings.CONFIGFILE

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
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info', '-h', '--h', '--usage', '-usage', '--help', '-help', 'help'):
                return print_sub_get_help()

            # Configfile
            elif arg in ('-c', '-config', '--config'):
                i += 2
                configfile = abspath(expanduser(args[i - 1]))

            # Positional arguments and errors
            else:

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

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate
    #/* ----------------------------------------------------------------------- */#

    # Load and validate configfile
    run = controller.Controller(configfile)

    try:
        run.validate()
        vprint("Valid!")
    except IOError as e:
        vprint(str(e))
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    return 0


#/* ======================================================================= */#
#/*     Define print_sub_get_help() function
#/* ======================================================================= */#

def print_sub_get_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """
    # TODO: Populate help
    vprint("""

    """.format(__docname__, '-' * len(__docname__), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define subcommand_get() function
#/* ======================================================================= */#

def subcommand_get(subcommand_name, args):

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    if len(args) is 0:
        return print_sub_setup_help()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    configfile = settings.CONFIGFILE
    config_option = None

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
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info', '-h', '--h', '--usage', '-usage', '--help', '-help', 'help'):
                return print_sub_get_help()

            # Configfile
            elif arg in ('-c', '-config', '--config'):
                i += 2
                configfile = abspath(expanduser(args[i - 1]))

            # Positional arguments and errors
            else:

                i += 1

                # Catch option
                if config_option is None:
                    config_option = arg

                # Invalid arguments
                else:
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

    # Check section
    if config_option is None:
        bail = True
        vprint("ERROR: Need an option to get")

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Get the value
    #/* ----------------------------------------------------------------------- */#

    # Load and validate configfile
    run = controller.Controller(configfile)

    # Get the property/attribute
    if hasattr(run, config_option):
        vprint(getattr(run, config_option))

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    return 0


#/* ======================================================================= */#
#/*     Define print_sub_setup_help() function
#/* ======================================================================= */#

def print_sub_setup_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """
    # TODO: Populate help
    vprint("""

    """.format(__docname__, '-' * len(__docname__), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define subcommand_setup() function
#/* ======================================================================= */#

def subcommand_setup(subcommand_name, args):

    """
    Populate with stuff
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    if len(args) is 0:
        return print_sub_setup_help()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    overwrite_mode = False

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    configfile = None

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
                return print_sub_setup_help()

            # I/O settings
            elif arg in ('-overwrite', '--overwrite'):
                i += 1
                overwrite_mode = True

            # Positional arguments and errors
            else:

                i += 1

                # Catch configfile
                if configfile is None:
                    configfile = abspath(expanduser(arg))

                # Unrecognized arguments
                else:
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

    if subcommand_name == 'setup':
        return subcommand_setup(subcommand_name, subcommand_args)
    elif subcommand_name == 'get':
        return subcommand_get(subcommand_name, subcommand_args)
    elif subcommand_name == 'validate':
        return subcommand_validate(subcommand_name, subcommand_args)
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
