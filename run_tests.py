#!/usr/bin/env python


# =================================================================================== #
#
# New BSD License
#
# Copyright (c) 2014, Kevin D. Wurster
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * The names of its contributors may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# =================================================================================== #


"""
Automatic unittest runner
"""


import inspect
from os.path import basename, dirname
import sys
import unittest


#/* ======================================================================= */#
#/*     Define document level information
#/* ======================================================================= */#

__docname__ = basename(inspect.getfile(inspect.currentframe()))
__author__ = 'Kevin D. Wurster (GitHub.com/geowurster)'
__version__ = '0.5'
__release__ = '2014-09-04'
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
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
{0} [-v 0|1|2] [-d True|False]
    """.format(__docname__, ' ' * len(__docname__)))

    return 1


#/* ======================================================================= */#
#/*     Define print_long_usage() function
#/* ======================================================================= */#

def print_long_usage():

    """
    Print full commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print_usage()
    print("""
    -v -verbosity       Set verbosity level
                        [default: 2]
    -d -description     Print unittest descriptions
                        [default: False]
    """)

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

    print(__license__)

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

    print(__version__)

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
    """ % (__docname__, __version__, __release__))

    return 1


#/* ======================================================================= */#
#/*     Define string2type() function
#/* ======================================================================= */#

def string2type(i_val):

    """
    Convert an input string to a Python type
    """

    # Force value to Python type
    try:
        return int(i_val)
    except ValueError:
        try:
            return float(i_val)
        except ValueError:
            if i_val.lower() == 'true':
                return True
            elif i_val.lower() == 'false':
                return False
            elif i_val.lower() == 'none':
                return None
            else:
                return i_val


#/* ======================================================================= */#
#/*     Define run_tests() function
#/* ======================================================================= */#

def run_tests(path=dirname(__file__), stream=sys.stderr, descriptions=True, verbosity=2):

    """
    Function to discover and run all unit tests

    :param stream: output stream
    :type stream: file
    :param descriptions: determines whether tests are printed or not
    :type descriptions: bool
    :param verbosity: specifies how verbose test responses are
    :type verbosity: int
    :rtype: unittest.runner.TextTestResult
    """

    # Discover tests
    test_suite = unittest.TestLoader().discover(path)

    # Run tests
    result = unittest.TextTestRunner(stream=stream, descriptions=descriptions, verbosity=verbosity).run(test_suite)

    return result



#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
Unittest structure: vessel_info.tests.run_tests()

def run_tests(path=dirname(__file__), stream=sys.stderr, descriptions=True, verbosity=2):

    '''
    Function to discover and run all unit tests
    '''

    # Discover tests
    test_suite = unittest.TestLoader().discover(path)

    # Run tests
    result = unittest.TextTestRunner(stream=stream, descriptions=descriptions, verbosity=verbosity).run(test_suite)

    return result
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    # Set defaults
    verbosity = 2
    descriptions = True
    discover_path = './'

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse arguments
    #/* ----------------------------------------------------------------------- */#

    # Parse arguments
    i = 0
    arg = None
    arg_error = False
    while i < len(args):

        try:
            arg = args[i]

            # Help arguments
            if arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo', '-h'):
                return print_help_info()
            elif arg in ('--license', '-license'):
                return print_license()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--long-usage', '-long-usage'):
                return print_long_usage()

            # Unittest configuration
            elif arg in ('-v', '-verbosity'):
                i += 2
                verbosity = string2type(args[i - 1])
            elif arg in ('-d', '-descriptions'):
                i += 2
                descriptions = string2type(args[i - 1])

            # Positional arguments and errors
            else:

                # Invalid argument
                i += 1
                discover_path = arg

        # This catches several conditions:
        #   1. The last argument is a flag that requires parameters but the user did not supply the parameter
        #   2. The arg parser did not properly consume all parameters for an argument
        #   3. The arg parser did not properly iterate the 'i' variable
        #   4. An argument split on '=' doesn't have anything after '=' - e.g. '--output-file='
        except (IndexError, ValueError):
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters: %s" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate / transform parameters
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check descriptions
    if descriptions not in (True, False):
        bail = True
        print("ERROR: Invalid descriptions: %s" % descriptions)

    # Check verbosity
    if verbosity not in range(3):
        bail = True
        print("ERROR: Invalid verbosity: %s" % verbosity)

    # Found an error - exit
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Run tests
    #/* ----------------------------------------------------------------------- */#

    # Run all tests
    print("Running tests...")
    print("  verbosity = %s" % verbosity)
    print("  descriptions = %s" % descriptions)
    print("  path = %s" % discover_path)

    # Execute tests
    try:
        result = run_tests(path=discover_path, stream=sys.stdout, descriptions=descriptions, verbosity=verbosity)
    except Exception, e:
        print(e)
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup / final return
    #/* ----------------------------------------------------------------------- */#

    # Make sure some tests actually ran
    if result.testsRun is 0:
        print("ERROR: Didn't run any tests\n")
        return 1

    # Figure out whether or not an error code should be returned
    if len(result.errors) > 0 or len(result.failures) > 0:
        return 1
    else:
        return 0


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
