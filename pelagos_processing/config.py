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
import os
import sys

import common
import settings


#/* ======================================================================= */#
#/*     Define show() function
#/* ======================================================================= */#

def show(configfile=settings.CONFIGFILE, stream=sys.stdout):

    """
    Print out the configfile contents.


    Args
    ----
    configfile : basestring
        Path to an existing configfile

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
#/*     Define _as_dict() function
#/* ======================================================================= */#

def _as_dict(configfile):

    """
    Why does this exist?

    The configfile parsing logic is needed in _as_dict() to convert the configfile
    to a dictionary and in is_clean() to determine if the configfile is actually
    properly formatted.  The ConfigParser() class only performs interpolation
    on read so the only way to ensure that all configfile sections and options
    are valid is to call ConfigParser.get() on each of them, which is essentially
    what as_dict() is doing, but is_clean() has to call as_dict(), which in turn
    calls is_clean() to ensure that the configfile it is trying to open is clean,
    which guarantees an exception.  The configfile is parsed with ConfigParser()
    instead of from_path() in order to avoid a similar circuitous situation.

    See as_dict.__doc__ for the actual documentation.

    Raises
    ------
    IOError
        If the configfile could not be loaded into a ConfigParser() instance
    """

    if isinstance(configfile, (str, unicode)) and os.access(configfile, os.R_OK):
        loaded = ConfigParser()
        loaded.read(configfile)
    elif isinstance(configfile, ConfigParser):
        loaded = configfile
    else:
        raise IOError("_as_dict() can't load: %s" % configfile)

    output = {}
    for section in loaded.sections():
        output[section] = {k: common.string2type(v) for k, v in loaded.items(section)}

    return output.copy()


#/* ======================================================================= */#
#/*     Define as_dict() function
#/* ======================================================================= */#

def as_dict(configfile):

    """
    Convert configfile to a dictionary.


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
    IOError
        If the input is a file path that doesn't exist

    ValueError
        If the ConfigParser class did not load the configfile.  Configfile
        not exist or user might not have read permission.
    """

    if isinstance(configfile, (str, unicode)) and os.access(configfile, os.R_OK) and is_clean(configfile):
        loaded = from_path(configfile)
    elif isinstance(configfile, ConfigParser):
        loaded = configfile
    else:
        raise IOError("Can't load configfile: %s" % configfile)

    try:
        return _as_dict(loaded).copy()
    except Exception:
        raise IOError("Can't load configfile: %s" % configfile)


#/* ======================================================================= */#
#/*     Define from_dict() function
#/* ======================================================================= */#

def from_dict(content):

    """
    Convert a dictionary to a ConfigParser instance.


    Arguments
    ---------
    content : dict
        Configfile content stored as a dictionary with sections as keys and
        and values set to dictionaries like {'option1': 'val1', 'option2': 'val2'}


    Returns
    -------
    ConfigParser
        A fully loaded instance of ConfigParser


    Raises
    ------
    TypeError
        If the input is not a dictionary
    """

    if not isinstance(content, dict):
        raise TypeError("Input must be a dictionary")

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
    Wrapper for ConfigParser.read() that performs some additional validations.


    Arguments
    ---------
    configfile_path : basestring
        Path to an existing configfile


    Returns
    -------
    ConfigParser
        A fully loaded instance of ConfigParser


    Raises
    ------
    IOError
        If the configfile could not be loaded
    """

    if not os.access(configfile_path, os.R_OK) or not is_clean(configfile_path):
        raise IOError("Can't load configfile: %s" % configfile_path)

    loaded = ConfigParser()
    result = loaded.read(configfile_path)
    if not result:
        raise IOError("Could not load configfile: %s" % configfile_path)

    return loaded


#/* ======================================================================= */#
#/*     Define is_clean() function
#/* ======================================================================= */#

def is_clean(configfile, raise_exception=False):

    """
    Determine whether or not a configfile can be safely used and expected to
    properly parse.


    Arguments
    ---------
    configfile : basestring
        Path to an existing configfile

    raise_exception : bool
        If the parse check fails, specify whether or not the offending exception
        should be thrown - otherwise False is returned


    Returns
    -------
    bool
        Configfile parsed properly if True and failed if False


    Raises
    ------
    A variety of exceptions
        Vary based on why the configfile could not be parsed.  Most likely
        exceptions are IOError if the file could not be loaded or a
        ConfigParser.InterpolationError if the configfile contains an improperly
        formatted interpolation.
    """

    try:
        _as_dict(configfile)
        return True
    except Exception as e:
        if raise_exception:
            raise e
        else:
            return False
