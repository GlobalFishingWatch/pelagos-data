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
Tools for processing vessel points
"""


import sys
try:
    from osgeo import ogr
except ImportError:
    import ogr
ogr.UseExceptions()

from . import io


#/* ======================================================================= */#
#/*     Define intersect_classification() function
#/* ======================================================================= */#

def _intersect(input_layer, intersect_layer, classification, f_name=None, f_width=None, f_type=None, f_precision=None):

    """
    Classify features in a layer if they intersect with features in another layer.
    The user must specify an input layer to be classified, an intersect layer
    against which the input layer is compared, and a classification value, which
    is used to update a field in the input layer whenever a feature is found
    to be intersecting with another feature


    :param input_layer: Layer object to be classified
    :type input_layer: ogr.Layer
    :param intersect_layer: Layer to check for intersecting geometries
    :type intersect_layer: ogr.Layer
    :param classification: value to be assigned to features
    :type classification: int|float|str|bool|None
    :param f_name: field to populate with the classification
    :type f_name: str
    :param f_width: OGR vector field width - only used if creating a field
    :type f_width: int
    :param f_type: OGR vector field type - only used if creating a field
    :type f_type: ogr.wkb*
    :param f_precision: OGR vector field precision - only used if creating a field
    :type f_precision: int

    :return: handle to input layer
    :rtype: ogr.Layer handle
    """

    # Handle defaults
    if f_name is None:
        f_name = 'class'
    if f_width is None:
        f_width = 254
    if f_type is None:
        f_type = ogr.OFTString

    # Make sure classification field is in the input layer - create if not
    field_names = [input_layer.GetLayerDefn().GetFieldDefn(i).GetName()
                   for i in range(input_layer.GetLayerDefn().GetFieldCount())]
    if f_name not in field_names:
        f_obj = ogr.FieldDefn(f_name, f_type)
        f_obj.SetWidth(f_width)
        if f_precision is not None:
            f_obj.SetPrecision(f_precision)
        input_layer.CreateField(f_obj)

    # Make sure the input layer is being read from the
    input_layer.ResetReading()
    COUNT = 0
    TOTAL = len(input_layer)
    for input_feature in input_layer:

        COUNT += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(COUNT), str(TOTAL)))
        sys.stdout.flush()

        # Get input geometry to compare
        input_geometry = input_feature.GetGeometryRef()

        # Make sure the intersect layer is being read from the first feature every time
        intersect_layer.ResetReading()
        for intersect_feature in intersect_layer:

            # Check intersect
            intersect_geometry = intersect_feature.GetGeometryRef()
            if input_geometry.Intersect(intersect_geometry):

                # Update the feature
                value = classification
                input_feature.SetField(f_name, value)
                input_layer.SetFeature(input_feature)

                # No need to look for more features since we already found one
                break

    # Cleanup
    input_geometry = None
    intersect_geometry = None
    input_feature = None
    intersect_feature = None
    input_layer.ResetReading()
    intersect_layer.ResetReading()

    return input_layer


#/* ======================================================================= */#
#/*     Define get_all_attributes() function
#/* ======================================================================= */#

def get_all_intersecting_attributes(lng, lat, layer):

    # Container to store all
    attributes = {}

    # Convert input lat/long to an ogr.Geometry() instance
    point = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (lng, lat))
    layer.ResetReading()
    for feature in layer:

        # Perform the intersect test
        geometry = feature.GetGeometryRef()
        if point.Intersect(geometry):

            # Add this FID and its attributes to the output dictionary
            attributes[feature.GetFID()] = io.get_attributes_as_dict(feature)

    # Reset reading on the input layer to return everything to its original state
    layer.ResetReading()
    geometry = None
    point = None
    feature = None

    return attributes.copy()
