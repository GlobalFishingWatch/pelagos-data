#!/usr/bin/env python


# This document is part of VesselInfo
# https://github.com/skytruth/VesselInfo


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
Unittests for pelagos_processing.cmdl.process_ais
"""


import os
from os.path import *
import sys
import unittest

from pelagos_processing import cmdl
from pelagos_processing.tests import testdata


class TestMain(unittest.TestCase):

    def setUp(self):
        self.output_test_file = '.OUTPUT-pelagos_processint_test_ProcESS_aIs.csv.ext'
        if isfile(self.output_test_file):
            os.remove(self.output_test_file)

    def tearDown(self):
        if isfile(self.output_test_file):
            os.remove(self.output_test_file)

    def test_standard(self):
        arguments = ['-q', testdata.process_ais_input14, self.output_test_file]
        exit_code = cmdl.process_ais.main(arguments)
        self.assertEqual(0, exit_code)
        with open(testdata.process_ais_output14, 'r') as expected_content:
            with open(self.output_test_file, 'r') as actual_content:
                for expected in expected_content:
                    actual = actual_content.readline()
                    self.assertEqual(expected, actual)


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main())
