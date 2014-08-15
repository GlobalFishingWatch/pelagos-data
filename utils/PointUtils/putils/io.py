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
Tools for transforming data into formats expected by PointUtils tools
"""


try:
    from osgeo import ogr
except ImportError:
    import ogr
ogr.UseExceptions()


#/* ======================================================================= */#
#/*     Define get_field_names() function
#/* ======================================================================= */#

def get_field_names(feature):

    """
    Get the field names for the given feature

    :param feature: an OGR feature object
    :type feature: ogr.Feature

    :return: field names for the given feature
    :rtype: list
    """

    return [feature.GetFieldDefnRef(i).GetName() for i in range(feature.GetFieldCount())]


#/* ======================================================================= */#
#/*     Define get_attributes_as_dict() function
#/* ======================================================================= */#

def get_attributes_as_dict(feature):

    """
    Take an ogr.Feature() instance and return all fields structured in a
    dictionary where the key is the field name and value is the attribute
    value found in the feature for that field.

    :param feature: an OGR feature
    :type feature: ogr.Feature

    :return: dictionary of key/val pairs
    :rtype: dict
    """

    return {i: feature.GetField(i) for i in get_field_names(feature)}.copy()


#/* ======================================================================= */#
#/*     Define get_layer() function
#/* ======================================================================= */#

def open_datasource(file_path, layer_name):

    # Get datasource
    ds = ogr.Open(file_path, 0)
    if ds is None:
        raise ValueError("ERROR: Could not read datasource: %s" % file_path)

    # Get layer
    layer = ds.GetLayerByName(layer_name)
    if layer is None:
        raise ValueError("ERROR: Could not read layer: %s" % layer_name)

    # Return both datasource and layer
    return ds, layer
