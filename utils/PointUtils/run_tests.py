#!/usr/bin/env python


# =================================================================================== #
#
#  New BSD License
#
#  Copyright (c) 2014, Kevin D. Wurster
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * The names of its contributors may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# =================================================================================== #


"""
Automatic test runner
"""


import inspect
from os import linesep
from os.path import basename
import os
import sys

import putils


#/* ======================================================================= */#
#/*     Build information
#/* ======================================================================= */#

__author__ = 'Kevin Wurster'
__version__ = '0.1'
__release__ = '2014-07-30'
__license__ = """
New BSD License

Copyright (c) 2014, Kevin D. Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of its contributors may not be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#

__docname__ = basename(inspect.getfile(inspect.currentframe()))


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline arguments, switches, and parameters

    :rtype: int
    """

    print("""
Usage: %s [options]

Options:
    --verbosity=0|1|2               Unittest verbosity level
    --descriptions=True|False       Print unittest descriptions
    --stream=file|stderr|stdout     Unittest output
    --stream-mode=w|a               Unittest output file write mode

Help Options:
    --license       Print license information
    --version       Print version information
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print out license information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print(__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_version():

    """
    Print script version information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
%s version %s - released %s
    """ % (__docname__, __version__, __release__))

    return 1


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def main(args):

    """
    Main routine

    :param args: arguments from the commandline (sys.argv[1:] in order to drop the script name)
    :type args: list

    :return: 0 on success and 1 on error
    :rtype: int
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults and containers
    #/* ----------------------------------------------------------------------- */#

    stream = 'stderr'
    stream_mode = 'w'
    stream_mode_options = ('w', 'a')
    stream_is_file = False
    verbosity = 2
    verbosity_options = (0, 1, 2)
    descriptions = True
    description_options = (True, False)

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse arguments
    #/* ----------------------------------------------------------------------- */#

    arg_error = False
    try:
        for arg in args:

            # Help arguments
            if arg in ('-usage', '--usage', '-help', '--help'):
                return print_usage()

            # Unittest configuration
            elif '--verbosity=' in arg:
                try:
                    verbosity = int(arg.split(arg, 1)[1])
                except ValueError:
                    arg_error = True
            elif '--descriptions=' in arg:
                descriptions = arg.split(arg, 1)[1].lower()
            elif '--stream=' in arg:
                stream = arg.split(arg, 1)[1].lower()
            elif '--stream-mode=' in arg:
                stream = arg.split(arg, 1)[1].lower()

            # Ignore empty arguments
            elif arg == '':
                pass

            # Catch errors
            else:
                print("ERROR: Invalid argument: %s" % str(arg))
                arg_error = True

    # Something went wrong - ran out of arguments
    except IndexError:
        arg_error = True
        print("ERROR: An argument has invalid parameters")

    #/* ----------------------------------------------------------------------- */#
    #/*     Adjust arguments
    #/* ----------------------------------------------------------------------- */#

    # Figure out if stream is a file or stderr|stdout
    # If its stderr|stdout, convert to the proper type
    original_stream = stream
    if stream == 'stderr':
        stream = sys.stderr
    elif stream == 'stdout':
        stream = sys.stdout
    else:
        stream_is_file = True

    # Adjust descriptions to python type
    if descriptions == 'true':
        descriptions = True
    elif descriptions == 'false':
        descriptions = False

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate configuration
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check unittest arguments
    if verbosity not in verbosity_options:
        bail = True
        print("ERROR: Invalid verbosity: %s" % str(verbosity))
        print("  Valid options: %s" % str(verbosity_options))
    if descriptions not in description_options:
        bail = True
        print("ERROR: Invalid descriptions parameter: %s" % descriptions)
        print("  Valid options: %s" % str(description_options))

    # Check stream/file
    if stream_is_file and not os.access(stream, os.W_OK):
        bail = True
        print("ERROR: Can't access: %s" % stream)
    if stream_is_file and stream_mode not in stream_mode_options:
        bail = True
        print("ERROR: Invalid stream mode: %s" % stream_mode)
        print("  Valid options: %s" % str(stream_mode_options))

    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Run tests
    #/* ----------------------------------------------------------------------- */#

    stream.write(linesep)
    stream.write("Running tests...%s" % linesep)
    stream.write("  verbosity = %s%s" % (verbosity, linesep))
    stream.write("  descriptions = %s%s" % (descriptions, linesep))
    stream.write("  stream = %s%s" % (original_stream, linesep))
    if stream_is_file:
        stream.write("stream_mode = %s%s" % (stream_mode, linesep))
    stream.write(linesep)

    # Open output file, if used
    if stream_is_file:
        stream = open(stream, stream_mode)

    # Execute tests
    result = putils.tests.run_tests(stream=stream, descriptions=descriptions, verbosity=verbosity)

    # Make sure some tests actually ran
    if result.testsRun is 0:
        stream.write("ERROR: Didn't run any tests%s" % linesep)
        if stream_is_file:
            stream.close()
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    # Close output file, if used
    if stream_is_file:
        stream.close()

    # Figure out whether or not an error code should be returned
    if len(result.errors) > 0 or len(result.failures) > 0:
        return 1
    else:
        return 0


#/* ======================================================================= */#
#/*     Commandline Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # No need to print usage if no arguments are supplied
    # Default behavior is discovering unittests and running
    sys.exit(main(sys.argv[1:]))
