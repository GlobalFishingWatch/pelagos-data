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
Unittests for vessel_info.settings
"""


from __future__ import unicode_literals


import os
from os.path import isfile
from pprint import pprint
import sys
import unittest

from vessel_info import settings
from vessel_info.tests import testdata


#/* ======================================================================= */#
#/*     Define TestWriteConfig() function
#/* ======================================================================= */#

class TestWriteConfig(unittest.TestCase):

    def setUp(self):
        r = reload(settings)

    def tearDown(self):
        r = reload(settings)

    def test_load(self):

        # Assuming the install went smoothly, the included configfile should already be loaded
        self.assertIsInstance(settings.CONFIG, dict)

        # Cache the loaded configfile and call the load and cache the new value
        original_config = settings.CONFIG.copy()
        expected = settings.load_configfile(configfile=testdata.configfile)
        actual = settings.CONFIG.copy()
        self.assertNotEqual(original_config, expected)
        self.assertDictEqual(expected, actual)

    def test_nonexistent_configfile(self):
        self.assertRaises(IOError, settings.load_configfile, configfile='bADN-asdjerCONFIG')

    def test_append(self):
        original = settings.CONFIG.copy()
        result = settings.load_configfile(configfile=testdata.configfile, append=True)
        actual = settings.CONFIG.copy()
        expected = dict(result.items() + original.items())
        self.assertDictEqual(expected, actual)
        self.assertNotEqual(actual, original)


#/* ======================================================================= */#
#/*     Define TestLoadConfig() function
#/* ======================================================================= */#

class TestLoadConfig(unittest.TestCase):

    def setUp(self):
        self.test_file = '.TestLoadConfig_TeStTFIELSDFa.cfg.ext'
        if isfile(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if isfile(self.test_file):
            os.remove(self.test_file)

    def test_write(self):

        test_dict = {
            'Section1': {
                'key1': 'val1',
                'key2': 'val2'
            }
        }

        settings.write_configfile(test_dict, self.test_file)
        loaded = settings.load_configfile(configfile=self.test_file, populate_global=False)

        # The test dictionary should match the one returned by the load
        # The one pre-loaded by settings should not match the test
        self.assertDictEqual(test_dict, loaded)
        self.assertNotEqual(settings.CONFIG, test_dict)

        # Loading the new configfile should place it in the CONFIG variable
        loaded = settings.load_configfile(self.test_file)
        self.assertDictEqual(loaded, settings.CONFIG)


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main())
