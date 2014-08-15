# This document is part of the pelagos project
# https://github.com/skytruth/pelagos


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
Tests for putils.io
"""


from os.path import *
import unittest

import putils
import testdata

try:
    from osgeo import ogr
except ImportError:
    import ogr
ogr.UseExceptions()


#/* ======================================================================= */#
#/*     Define TestOpenDatasource() class
#/* ======================================================================= */#

class TestDataSource(unittest.TestCase):

    def setUp(self):
        self.t_ds = ogr.Open(testdata.polygon_shapefile)
        self.assertIsNotNone(self.t_ds)
        self.t_layer = self.t_ds.GetLayerByName(basename(testdata.polygon_shapefile).split('.',)[0])
        self.assertIsNotNone(self.t_layer)

    def tearDown(self):
        self.t_layer = None
        self.t_ds = None

    def test(self):

        # Open with wrapper
        ds, layer = putils.io.open_datasource(testdata.polygon_shapefile, self.t_layer.GetName())
        self.assertIsNotNone(ds)
        self.assertIsNotNone(layer)

        # Simple test to make sure both have the same number of layers and features
        self.assertEqual(len(self.t_ds), len(ds))
        self.assertEqual(len(self.t_layer), len(layer))


#/* ======================================================================= */#
#/*     Define TestGetAttributesAsDict() class
#/* ======================================================================= */#

class TestGetAttributesAsDict(unittest.TestCase):

    def setUp(self):
        self.polygon_ds = ogr.Open(testdata.polygon_shapefile)
        self.assertIsNotNone(self.polygon_ds)
        self.polygon_layer = self.polygon_ds.GetLayerByName(basename(testdata.polygon_shapefile).split('.',)[0])
        self.assertIsNotNone(self.polygon_layer)

    def tearDown(self):
        self.polygon_layer = None
        self.polygon_ds = None

    def test(self):

        # Test all features
        self.polygon_layer.ResetReading()
        for feature in self.polygon_layer:
            field_names = [feature.GetFieldDefnRef(i).GetName() for i in range(feature.GetFieldCount())]
            expected = {i: feature.GetField(i) for i in field_names}
            actual = putils.io.get_attributes_as_dict(feature)
            self.assertDictEqual(expected, actual)

        # Cleanup
        feature = None


#/* ======================================================================= */#
#/*     Define TestGetFieldNames() class
#/* ======================================================================= */#

class TestGetFieldNames(unittest.TestCase):

    def setUp(self):
        self.polygon_ds = ogr.Open(testdata.polygon_shapefile)
        self.assertIsNotNone(self.polygon_ds)
        self.polygon_layer = self.polygon_ds.GetLayerByName(basename(testdata.polygon_shapefile).split('.',)[0])
        self.assertIsNotNone(self.polygon_layer)

    def tearDown(self):
        self.polygon_layer = None
        self.polygon_ds = None

    def test(self):

        self.polygon_layer.ResetReading()
        for feature in self.polygon_layer:
            expected = [feature.GetFieldDefnRef(i).GetName() for i in range(feature.GetFieldCount())]
            actual = putils.io.get_field_names(feature)
            self.assertListEqual(expected, actual)

        # Cleanup
        feature = None
