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
Configfile utilities
"""


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
import sys

import common
import settings


#/* ======================================================================= */#
#/*     Define show() function
#/* ======================================================================= */#

def show(configfile=settings.CONFIGFILE, stream=sys.stdout):

    """
    Print out the configfile contents

    Args
    ----
    stream : file
        Open file-like object where lines are written

    Returns
    -------
    list
        One element per configfile line
    None
        Error
    """

    with open(configfile, 'r') as f:
        lines = f.readlines()
        for line in lines:
            stream.write(line)

    return lines


#/* ======================================================================= */#
#/*     Define as_dict() function
#/* ======================================================================= */#

def as_dict(configfile):

    """
    Convert configfile to a dictionary

    Arguments
    ---------
    configfile : basestring
        Path to the configfile to use

    Returns
    -------
    dict
        Configfile sections are top level keys with sub-values as sub-keys::
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

    Raises
    ------
    ValueError
        If the ConfigParser class did not load the configfile.  Configfile
        not exist or user might not have read permission.
    """

    if isinstance(configfile, (str, unicode)):
        loaded = from_path(configfile)
    elif isinstance(configfile, ConfigParser):
        loaded = configfile
    else:
        loaded = from_path(configfile)

    output = {}
    for section in loaded.sections():
        output[section] = {k: common.string2type(v) for k, v in loaded.items(section)}

    return output.copy()


#/* ======================================================================= */#
#/*     Define from_dict() function
#/* ======================================================================= */#

def from_dict(content):

    """
    Convert a dictionary to a ConfigParser instance
    """

    if not isinstance(content, dict):
        raise ValueError("Input must be a dictionary")

    config = ConfigParser()

    for section in content.keys():
        config.add_section(section)
        for key, val in content[section].iteritems():
            config.set(section, key, val)

    return config


#/* ======================================================================= */#
#/*     Define from_path() function
#/* ======================================================================= */#

def from_path(configfile_path):

    """
    Convert a configfile to a ConfigParser instance
    """

    if not isinstance(configfile_path, (str, unicode)):
        raise ValueError("Configfile path must be a string type")

    loaded = ConfigParser()
    result = loaded.read(configfile_path)
    if not result:
        raise ValueError("Could not load configfile: %s" % configfile_path)

    return loaded
