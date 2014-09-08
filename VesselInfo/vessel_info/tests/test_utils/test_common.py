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
Unittests for vessel_info.utils.common
"""


from __future__ import unicode_literals

import sys
import unittest

from vessel_info import utils


#/* ======================================================================= */#
#/*     Define TestString2Type() class
#/* ======================================================================= */#

class TestString2Type(unittest.TestCase):

    def test_standard(self):

        self.assertEqual(utils.common.string2type('1'), 1)
        self.assertEqual(utils.common.string2type('1.23'), 1.23)

        self.assertTrue(utils.common.string2type('True'))
        self.assertTrue(utils.common.string2type('TRUE'))
        self.assertTrue(utils.common.string2type('TRuE'))
        self.assertTrue(utils.common.string2type('true'))

        self.assertFalse(utils.common.string2type('False'))
        self.assertFalse(utils.common.string2type('FALSE'))
        self.assertFalse(utils.common.string2type('FALsE'))
        self.assertFalse(utils.common.string2type('false'))

        self.assertEqual(utils.common.string2type('None'), None)
        self.assertEqual(utils.common.string2type('NONE'), None)
        self.assertEqual(utils.common.string2type('NOnE'), None)
        self.assertEqual(utils.common.string2type('none'), None)

        expected = {'key1': ['e1', 'e2', 'e3'], 'key2': 'VAL2'}
        actual = utils.common.string2type('{"key2": "VAL2", "key1": ["e1", "e2", "e3"]}')
        self.assertDictEqual(expected, actual)

        self.assertEqual(utils.common.string2type('String'), 'String')
        self.assertEqual(utils.common.string2type('STRING'), 'STRING')
        self.assertEqual(utils.common.string2type('STRiNG'), 'STRiNG')
        self.assertEqual(utils.common.string2type('string'), 'string')
        self.assertEqual(utils.common.string2type('True False None 1 1.23 {"key2": "VAL2", "key1": ["e1", "e2", "e3"]}'),
                         'True False None 1 1.23 {"key2": "VAL2", "key1": ["e1", "e2", "e3"]}')


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main())
