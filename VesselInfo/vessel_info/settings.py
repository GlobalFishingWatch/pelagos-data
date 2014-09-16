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
Module-wide settings and options
"""


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
import os
import sys

from . import assets


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__module_name__ = 'VesselInfo'
__version__ = '0.1-dev'
__release__ = '2014-09-02'
__author__ = 'Kevin Wurster'
__author_email__ = 'kevin@skytruth.org'
__source__ = 'https://github.com/SkyTruth/pelagos-data/'
__license__ = """
The MIT License (MIT)

Copyright (c) 2014 SkyTruth

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


#/* ======================================================================= */#
#/*     Defaults and global settings
#/* ======================================================================= */#

STREAM = sys.stdout


#/* ======================================================================= */#
#/*     Define print_configfile() function
#/* ======================================================================= */#

def print_configfile(verbose=True, stream=STREAM, *args):

    """
    Print out the contents of the configfile


    Args:

        Position 0: Optional configfile - defaults to assets.configfile


    Kwargs:

        verbose     (bool): Specify whether or not the configfile content
                            should be printed.  If False nothing will be
                            printed but all lines will be returned.

        stream      (file): Specify where the lines should be printed/written.
                            Any class with a .write() method can also be used.


    Returns:

        [
            '[FleetMon]\n',
            'user = None\n',
            'key = None\n'
        ]


    Raises:

        IOError: When configfile could not be loaded - means ConfigParser failed
                 or the configfile could not be found
    """

    if len(args) > 0:
        configfile = args[0]
    else:
        configfile = assets.configfile

    with open(configfile, 'r') as f:
        output = [line for line in f.readlines()]

        if verbose:
            for line in output:
                stream.write(line)

        return output


#/* ======================================================================= */#
#/*     Define load_configfile() function
#/* ======================================================================= */#

def load_configfile(populate_global=True, *args):

    """
    Convert configfile to a dictionary and store in a global variable for access

    Args:

        Position 0: Optional configfile - defaults to assets.configfile


    Kwargs:

        populate_global    (bool): Specify whether or not the global CONFIG variable
                                   should be set to output dictionary


    Returns:

        {
            'Section1': {
                'key1': 'val1',
                'key2': 'val2',
            },
            'Section2': {
                'key1': 'val1',
                'key2': 'val2',
            }
        }


    Raises:

        IOError: When configfile could not be loaded - means ConfigParser failed
                 or the configfile could not be found
    """

    global CONFIG

    if len(args) > 0:
        configfile = args[0]
    else:
        configfile = assets.configfile

    loaded = ConfigParser()
    result = loaded.read(configfile)
    if not result:
        raise IOError("Could not load configfile: %s" % configfile)

    output = {}
    for section in loaded.sections():
        output[section] = {k: v for k, v in loaded.items(section)}

    if populate_global:
        CONFIG = output.copy()

    return output.copy()


# Load the configfile
try:
    CONFIG = load_configfile()
except IOError:
    CONFIG = None
