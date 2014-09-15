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
Unittests and test runner
"""


from os.path import dirname
import sys
import unittest

import testdata
import test_scrape


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
