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
Tests for putils.classify
"""


import csv
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
#/*     Define TestGetAllIntersectingAttributes() class
#/* ======================================================================= */#

class TestGetAllIntersectingAttributes(unittest.TestCase):

    def setUp(self):
        self.polygon_ds = ogr.Open(testdata.polygon_shapefile)
        self.assertIsNotNone(self.polygon_ds)
        self.polygon_layer = self.polygon_ds.GetLayerByName(basename(testdata.polygon_shapefile).split('.',)[0])
        self.assertIsNotNone(self.polygon_layer)

    def tearDown(self):
        self.polygon_layer = None
        self.polygon_ds = None

    def test(self):

        # Assemble the expected output
        expected = []
        with open(testdata.point_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                point = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (row['long'], row['lat']))
                self.polygon_layer.ResetReading()
                attributes = {}
                for feature in self.polygon_layer:
                    polygon = feature.GetGeometryRef()
                    if point.Intersect(polygon):
                        attributes = {feature.GetFID(): putils.io.get_attributes_as_dict(feature)}
                expected.append(attributes)

        # Assemble the actual output
        with open(testdata.point_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:

                # Get the actual output from the function
                actual = putils.classify.get_all_intersecting_attributes(row['long'], row['lat'], self.polygon_layer)

                # Assemble the expected output
                expected = {}
                point = ogr.CreateGeometryFromWkt("POINT(%s %s)" % (row['long'], row['lat']))
                self.polygon_layer.ResetReading()
                for feature in self.polygon_layer:

                    # Geometry test
                    if point.Intersect(feature.GetGeometryRef()):
                        expected[feature.GetFID()] = putils.io.get_attributes_as_dict(feature)

                # Run test
                self.assertDictEqual(expected, actual)


        # Cleanup
        point = None
        feature = None
