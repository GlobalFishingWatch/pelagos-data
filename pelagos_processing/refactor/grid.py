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
Grid processing
"""


try:
    from osgeo import ogr
except ImportError:
    import ogr
ogr.UseExceptions()


def collect_layer_geometry(input_layer, hull=False):

    output_geometry = ogr.Geometry(ogr.wkbGeometryCollection)
    input_layer.ResetReading()
    for feature in input_layer:
        if hull:
            output_geometry.AddGeometry(feature.GetGeometryRef().ConvexHull)
        else:
            output_geometry.AddGeometry(feature.GetGeometryRef)

    # Cleanup
    feature = None

    return output_geometry.Clone()




def grid_geometry(input_geom, grid_layer, o_layer, constrain='hull'):

    output_geoms = []

    grid_layer.ResetReading()

    if constrain is not None:
        if constrain is True or constrain.lower() == 'hull':
            grid_layer.SetSpatialIndex(input_geom.ConvexHull)
        else:
            grid_layer.SetSpatialIndex(input_geom)

    for grid_feature in grid_layer:
        grid_geom = grid_feature.GetGeometryRef()
        intersecting_geom = grid_geom.Intersection(input_geom)

        # Only add to output if the resulting geometry actually contains stuff
        if not intersecting_geom.IsEmpty():

            # If a vertex of the input geometry falls on a line segment of an input geometry then a geometry collection
            # containing non-polygon geometries is returned.  If this happens, the non-polygons need to be removed
            if intersecting_geom.GetGeometryType() is ogr.wkbGeometryCollection:
                temp_geom = ogr.Geometry(ogr.wkbMultiPolygon)
                for i in range(intersecting_geom.GetGeometryCount()):
                    sub_geom = intersecting_geom.GetGeometryRef(i)
                    if sub_geom.GetGeometryType() not in (-2147483648, -2147483647, -2147483646, -2147483644,
                                                          -2147483643, -2147483641, 0, 1, 2, 4, 5, 7, 100, 101):
                        temp_geom.AddGeometry(sub_geom)
                intersecting_geom = temp_geom

            # The above edge case could ONLY contain non-polygon geometries so another test is required
            if not intersecting_geom.IsEmpty():
                output_geoms.append(intersecting_geom)

    # Cleanup
    grid_layer.ResetReading()
    grid_geom = None
    grid_feature = None
    temp_geom = None
    sub_geom = None
    if constrain is not None:
        grid_layer.RemoveSpatialIndex()

    return output_geoms
