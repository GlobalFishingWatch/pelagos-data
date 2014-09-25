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


from __future__ import unicode_literals

import logging
import sys


#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#
__all__ = ['__module_name__', '__version__', '__release__', '__author__', '__author_email__', '__source__', '__license__',
           'MIN_FISHING_SCORE', 'MAX_FISHING_SCORE', 'MAX_ZOOM', 'MIN_SCORE', 'MAX_SCORE', 'MAX_INTERVAL', 'TYPE_NORMAL',
           'TYPE_SEGMENT_START', 'TYPE_SEGMENT_END', 'STREAM', 'CONFIGFILE', 'logging']


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__module_name__ = 'PelagosProcessing'
__version__ = '0.1-dev'
__release__ = '2014-09-1'
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
#/*     Scores
#/* ======================================================================= */#

MIN_FISHING_SCORE = -15.0
MAX_FISHING_SCORE = 5.0
MAX_ZOOM = 15
MIN_SCORE = -15.0
MAX_SCORE = 5.0
MAX_INTERVAL = 24 * 60 * 60  # 24 hours
TYPE_NORMAL = 0
TYPE_SEGMENT_START = 1
TYPE_SEGMENT_END = 2


#/* ======================================================================= */#
#/*     Default logging and streams
#/* ======================================================================= */#

STREAM = sys.stdout
CONFIGFILE = 'Config.cfg'
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
