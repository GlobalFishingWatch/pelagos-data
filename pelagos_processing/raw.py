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
Vessel processing
"""


from __future__ import unicode_literals

import os


#/* ======================================================================= */#
#/*     Global variables
#/* ======================================================================= */#

RAW_SCHEMA = ['mmsi', 'longitude', 'latitude', 'timestamp', 'score', 'navstat', 'hdg', 'rot', 'cog', 'sog']


#/* ======================================================================= */#
#/*     Define cat_files() function
#/* ======================================================================= */#

def cat_files(input_files, target_file, schema=RAW_SCHEMA, write_mode='w', skip_lines=0, skip_empty=False):

    """
    Concatenate a large number of large files


    Kwargs
    ------
    input_files : list, tuple
        List of input files to concatenate

    target_file : str, unicode
        File to concatenate into

    schema : str, list, tuple, None
        Output file header.  Strings are joined with ','.join(schema).  Use
        None or '' to skip writing header.

    write_mode : str
        Mode used in open() to edit output file

    skip_lines : int
        Number of lines to skip in each input file

    skip_empty : bool
        Skip empty lines, which are classified as line in ('', os.linesep)


    Returns
    -------
    True
        Success

    Raises
    ------
    ValueError
        Invalid argument value
    TypeError
        Invalid argument type
    IOError
        An input file does not exist or user does not have read access
    """

    # Transform and validate arguments
    write_mode = write_mode.lower()
    if not isinstance(skip_lines, int) or not skip_lines >= 0:
        raise ValueError("Invalid skip lines - must be an int >= 0: %s" % skip_lines)
    if isinstance(schema, (list, tuple)):
        header = ','.join(schema)
    elif isinstance(schema, (str, unicode, None)):
        header = schema
    else:
        raise TypeError("Invalid schema: %s" % schema)

    # Make sure all the input files actually exist
    for ifile in input_files:
        if not os.access(ifile, os.R_OK):
            raise IOError("Can't access input file: %s" % ifile)

    with open(target_file, write_mode) as o_f:

        # Write the header if specified
        if schema not in (None, ''):
            o_f.write(header + os.linesep)

        for ifile in input_files:
            with open(ifile) as i_f:
                # Skip lines
                for sl in range(skip_lines):
                    i_f.next()
                for line in i_f:
                    if not skip_empty and line not in ('', os.linesep):
                        o_f.write(line)

    return True
