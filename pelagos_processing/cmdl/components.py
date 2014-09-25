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
Common components for all commandline utilities
"""


import json
from os import linesep
from .. import settings


#/* ======================================================================= */#
#/*     Global variables
#/* ======================================================================= */#

VERBOSE_MODE = True
DEFAULT_STREAM = settings.STREAM


#/* ======================================================================= */#
#/*     Document level attributes
#/* ======================================================================= */#

__all__ = ['print_version', 'print_short_version', 'print_license', 'print_help_info', 'vprint', 'string2type']


#/* ======================================================================= */#
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags


    Returns:

        1 for exit code purposes
    """

    global DEFAULT_STREAM

    DEFAULT_STREAM.write("""
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
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print licensing information


    Returns:

        1 for exit code purposes
    """

    global DEFAULT_STREAM

    DEFAULT_STREAM.write(settings.__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_short_version():

    """
    Only print the module version


    Returns:

        1 for exit code purposes
    """

    global DEFAULT_STREAM

    DEFAULT_STREAM.write(settings.__version__ + linesep)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_version():

    """
    Print the module version and release date


    Returns:

        1 for exit code purposes
    """

    global DEFAULT_STREAM

    DEFAULT_STREAM.write("""
%s v%s released %s

""" % (settings.__module_name__, settings.__version__, settings.__release__))

    return 1


#/* ======================================================================= */#
#/*     Define vprint() function
#/* ======================================================================= */#

def vprint(message, stream=DEFAULT_STREAM, flush=False):

    """
    Easily handle verbose printing.  Newline characters are automatically
    appended if they are not already present.


    Arguments:

        message (str|unicode|list|tuple):   A single or multi-line message to be
                                            written to the specified stream. If
                                            the input datatype is a list or tuple,
                                            each element is assumed to be a line
                                            of the message and are written
                                            separately.
        stream (file):  An open file or other object with a callable "write()"
                        [default: sys.stdout]
    """

    global VERBOSE_MODE
    global DEFAULT_STREAM

    if VERBOSE_MODE:

        # Configure the stream
        if stream is None or isinstance(stream, (str, unicode)) and stream.lower() == 'default':
            stream = DEFAULT_STREAM

        # Wrap single line messages
        if not isinstance(message, (list, tuple)):
            message = [message]

        # Assemble message into a single block of text
        o_message = ''
        for line in message:

            # Check if line is just supposed to be a return
            if len(line) is 0:
                line = linesep
            elif line[-1] != linesep:
                line += linesep

            o_message += line

        # Write to stream
        if flush:
            if o_message[-1] == linesep:
                o_message = o_message[:-1]
            stream.write(o_message)
            stream.flush()
        else:
            stream.write(o_message)
