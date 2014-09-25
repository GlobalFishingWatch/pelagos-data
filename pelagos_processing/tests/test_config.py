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
Unittests for pelagos_processing.config
"""


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
import unittest

from pelagos_processing import config
from pelagos_processing.tests import testdata
from pelagos_processing import common


class DevNull(object):

    @staticmethod
    def write(self, *args, **kwargs):
        pass


class TestConfig(unittest.TestCase):

    def test_show(self):
        with open(testdata.sample_config) as f:
            actual = f.readlines()
        expected = config.show(testdata.sample_config, DevNull)
        self.assertEqual(expected, actual)

    def test_as_from_series(self):
        parsed = ConfigParser()
        parsed.read(testdata.sample_config)
        self.assertDictEqual(config.as_dict(parsed), config.as_dict(testdata.sample_config))
        self.assertDictEqual(config.as_dict(parsed), config.as_dict(config.from_path(testdata.sample_config)))

        as_dictionary = config.as_dict(testdata.sample_config)
        
        for section in parsed.sections():
            self.assertIn(section, as_dictionary)
            for option in parsed.options(section):
                self.assertEqual(common.string2type(parsed.get(section, option)), as_dictionary[section][option])

    def test_as_dict_from_path(self):
        loaded = config.as_dict(testdata.sample_config)
        self.assertIn('section1', loaded)
        self.assertIsInstance(loaded, dict)
        self.assertRaises(ValueError, config.from_path, 'not a path--^^')

    def test_as_dict_from_configparser(self):
        loaded = config.as_dict(testdata.sample_config)
        self.assertIn('section1', loaded)
        self.assertIsInstance(loaded, dict)
        self.assertRaises(ValueError, config.from_path, 1.23)  # Not a path or ConfigParser instance

    def test_from_dict(self):
        config_dict = {
            'section1': {
                'key1': 'val1',
                'integer': 1
            }
        }
        loaded = config.from_dict(config_dict)
        self.assertTrue(loaded.has_section('section1'))
        self.assertIsInstance(loaded, ConfigParser)
        self.assertRaises(ValueError, config.from_path, 'not a dictionary')

    def test_from_path(self):
        loaded = config.from_path(testdata.sample_config)
        self.assertTrue(loaded.has_section('section1'))
        self.assertIsInstance(loaded, ConfigParser)
        self.assertRaises(ValueError, config.from_path, '.--asBad_PAA~~~th')
