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
Unittests for pelagos_processing.raw
"""


from __future__ import unicode_literals

import os
from os.path import isfile
import unittest

from pelagos_processing import raw
from pelagos_processing.tests import testdata


class DevNull(object):

    @staticmethod
    def write(self, *args, **kwargs):
        pass


class TestCatFiles(unittest.TestCase):

    def setUp(self):
        self.input_files = (testdata.cat1, testdata.cat2, testdata.cat3, testdata.cat4)
        self.test_file = '.TestCatFiles_standard--a--.csv.ext'
        if isfile(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if isfile(self.test_file):
            os.remove(self.test_file)

    def test_standard(self):

        schema = ['uid', 'val']
        expected = ','.join(schema) + os.linesep
        for ifile in self.input_files:
            with open(ifile) as f:
                for line in f:
                    expected += line

        self.assertTrue(raw.cat_files(self.input_files, self.test_file, schema=schema, write_mode='w'))
        with open(self.test_file) as f:
            actual = f.read()
        self.assertEqual(expected, actual)

    def test_skipline(self):

        skip = 1
        schema = 'uid,val'
        expected = schema + os.linesep
        for ifile in self.input_files:
            with open(ifile) as f:
                for sl in range(skip):
                    f.next()
                for line in f:
                    expected += line

        self.assertTrue(raw.cat_files(self.input_files, self.test_file, schema=schema, write_mode='w', skip_lines=skip))
        with open(self.test_file) as f:
            actual = f.read()
        self.assertEqual(expected, actual)

    def test_exceptions(self):
        self.assertRaises(ValueError, raw.cat_files, *[self.input_files, self.test_file], **{'skip_lines': -1})
        self.assertRaises(ValueError, raw.cat_files, *[self.input_files, self.test_file], **{'skip_lines': None})
        self.assertRaises(TypeError, raw.cat_files, *[self.input_files, self.test_file], **{'schema': 1.23})
        self.assertRaises(IOError, raw.cat_files, *[['I-DO_NOT_|EXIST'], self.test_file])
