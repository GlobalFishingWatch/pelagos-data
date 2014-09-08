#!/usr/bin/env python


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
Unittests for vessel_info.utils.compare_scrape
"""


from __future__ import unicode_literals

import os
from os.path import isfile
import sys
import unittest

from vessel_info.tests import testdata
from vessel_info import utils


#/* ======================================================================= */#
#/*     Define TestCompareScrape() function
#/* ======================================================================= */#

class TestFile2Dict(unittest.TestCase):

    def test_standard(self):

        test_file = testdata.sample_mmsi

        expected = {
            '209107000': {'mmsi': '209107000'},
            '209108000': {'mmsi': '209108000'},
            '209109000': {'mmsi': '209109000'},
            '209110000': {'mmsi': '209110000'},
            '209118000': {'mmsi': '209118000'},
            '209121000': {'mmsi': '209121000'},
            '209128000': {'mmsi': '209128000'},
            '209135000': {'mmsi': '209135000'},
            '209136000': {'mmsi': '209136000'},
            '209154000': {'mmsi': '209154000'},
        }
        actual = utils.compare_scrape.file2dict('mmsi', test_file)
        self.assertEqual(expected, actual)


#/* ======================================================================= */#
#/*     Define TestMain() function
#/* ======================================================================= */#

class TestMain(unittest.TestCase):

    def setUp(self):
        self.test_file = '.deleteme_TEST_FILE_test_common_TestMain.csv'
        if isfile(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if isfile(self.test_file):
            os.remove(self.test_file)

    def test_standard(self):

        # Assemble components
        input_file1 = testdata.test_common_TestMain_test_standard_input1
        input_file2 = testdata.test_common_TestMain_test_standard_input2
        output_file = self.test_file
        expected_output_file = testdata.test_common_TestMain_test_standard_expected_output

        # Call main
        args = ['-q', '-mf', 'mmsi', '-cf', 'cfield', '-omf', 'Ommsi', input_file1, input_file2, output_file]
        self.assertEqual(0, utils.compare_scrape.main(args))

        # Cache the expected and actual files as a comparable dictionary then compare
        actual_dict = utils.compare_scrape.file2dict('Ommsi', output_file)
        expected_dict = utils.compare_scrape.file2dict('Ommsi', expected_output_file)
        self.assertDictEqual(actual_dict, expected_dict)


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main())
