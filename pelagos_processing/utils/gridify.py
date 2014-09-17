#!/usr/bin/env python


# This document is part of Pelagos Data
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
Clip arbitrary regions to quad tree levels
"""


import inspect
import os
from os.path import *
import sys

import common
from common import *

try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr
ogr.UseExceptions()
osr.UseExceptions()


#/* ======================================================================= */#
#/*     Document level information
#/* ======================================================================= */#

__all__ = ['print_usage', 'print_help', 'print_long_usage', 'main']
__docname__ = basename(inspect.getfile(inspect.currentframe()))


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Command line usage information

    :return: 1 for exit code purposes
    :rtype: int
    """
    # TODO: Populate usage
    vprint("""
Usage:
    {0} [-of ogr_driver] [-lco option=value] [-dsco option=value]
    {1} [-gl layer_name|layer1,layer2,...] [-rl layer_name|layer1,layer2]
    {1} --grid=grid_file.ext --region=region_file.ext -o output_file.ext
""".format(__docname__, " " * len(__docname__)))
    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """
    # TODO: Populate help
    vprint("""
Help: {0}
------{1}
{2}
    """.format(__docname__, '-' * len(__docname__), main.__doc__))

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: 1 for exit code purposes
    :rtype: int
    """

    vprint("""
Help flags:
    --help      More detailed description of this utility
    --usage     Arguments, parameters, flags, options, etc.
    --version   Version and ownership information
    --license   License information
    """)

    return 1


#/* ======================================================================= */#
#/*     Define ring2poly() function
#/* ======================================================================= */#

def ring2poly(ring, add_z=True):

    """
    Convert a linearring to a ogr.wkbPolygon
    """

    if not ring.GetGeometryType() is ogr.wkbLinearRing:
        raise ValueError("ERROR: Wrong type - should be '%s' not '%s'" % (ogr.wkbLinearRing, ring.GetGeometryType()))

    ring = ring.CLone()
    if add_z:
        geom_type = ogr.wkbPolygon
    else:
        geom_type = ogr.wkbPolygon25D

    temp_geom = ogr.Geometry(geom_type)
    temp_geom.AddGeometry(ring)
    return temp_geom.Clone()


#/* ======================================================================= */#
#/*     Define is_ring_poly() function
#/* ======================================================================= */#

def is_ring_poly(ring):

    """
    Determine whether or not a ogr.wkbLinearRing is closed, which means it could
    be a polygon
    """

    if not ring.GetGeometryType() is ogr.wkbLinearRing:
        raise ValueError("ERROR: Wrong type - should be '%s' not '%s'" % (ogr.wkbLinearRing, ring.GetGeometryType()))

    p_indexes = range(ring.GetPointCount())
    if ring.GetPoint(min(p_indexes)) == ring.GetPoint(max(p_indexes)):
        return True
    else:
        return False


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
    TODO: Populate docstring with --help readable information
    """

    # TODO: Populate docstring

    #/* ----------------------------------------------------------------------- */#
    #/*     Print usage
    #/* ----------------------------------------------------------------------- */#

    if len(args) is 0:
        return print_usage()

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    output_driver_name = "ESRI Shapefile"

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    grid_file = None
    grid_layer_name = None
    region_file = None
    region_layer_name = None
    output_file = None
    output_dsco = []
    output_lco = []

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse arguments
    #/* ----------------------------------------------------------------------- */#

    i = 0
    arg = None
    arg_error = False
    while i < len(args):

        try:
            arg = args[i]

            # Help arguments
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info', '-h', '--h'):
                return print_help_info()
            elif arg in ('--help', '-help'):
                return print_help()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--license', '-usage'):
                return print_license()

            # User feedback
            elif arg in ('-q', '-quiet'):
                i += 1
                common.VERBOSE_MODE = False

            # Specify input files
            elif arg in ('-g', '-grid'):
                i += 2
                grid_file = normpath(expanduser(args[i - 1]))
            elif arg in ('-gl', '-grid-layer'):
                i += 2
                grid_layer_name = args[i - 1]
            elif arg in ('-r', '-region'):
                i += 2
                region_file = normpath(expanduser(args[i - 1]))
            elif arg in ('-rl', '-region-layer'):
                i += 2
                region_layer_name = normpath(expanduser(args[i - 1]))

            # Output file
            elif arg in ('-o', '-outfile'):
                i += 2
                output_file = normpath(expanduser(args[i - 1]))

            # OGR output options
            elif arg in ('-of', '-output-format'):
                i += 2
                output_driver_name = normpath(expanduser(args[i - 1]))
            elif arg in ('-lco', '-lyr-creation-options'):
                i += 2
                output_lco.append(args[i - 1])
            elif arg in ('-dsco', '-ds-creation-options'):
                i += 2
                output_dsco.append(args[i - 1])

            # Positional arguments and errors
            else:

                # Invalid argument
                i += 1
                arg_error = True
                vprint("ERROR: Invalid argument: %s" % arg)

        # This catches several conditions:
        #   1. The last argument is a flag that requires parameters but the user did not supply the parameter
        #   2. The arg parser did not properly consume all parameters for an argument
        #   3. The arg parser did not properly iterate the 'i' variable
        #   4. An argument split on '=' doesn't have anything after '=' - e.g. '--output-file='
        except (IndexError, ValueError):
            i += 1
            arg_error = True
            vprint("ERROR: An argument has invalid parameters: %s" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate parameters
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        vprint("ERROR: Did not successfully parse arguments")

    # Check input driver name
    if not isinstance(output_driver_name, str):
        bail = True
        vprint("ERROR: Invalid output driver name: %s" % output_driver_name)

    # Check input grid file
    if not isinstance(grid_file, str):
        bail = True
        vprint("ERROR: Invalid input grid file: %s" % grid_file)
    elif not os.access(grid_file, os.R_OK):
        bail = True
        vprint("ERROR: Invalid input grid file: %s" % grid_file)

    # Check input region file
    if not isinstance(region_file, str):
        bail = True
        vprint("ERROR: Invalid input region file: %s" % region_file)
    elif not os.access(region_file, os.R_OK):
        bail = True
        vprint("ERROR: Can't access input region file: %s" % region_file)

    # Check output file
    if not isinstance(output_file, str):
        bail = True
        vprint("ERROR: Invalid output file: %s" % output_file)
    elif os.path.exists(output_file):
        bail = True
        vprint("ERROR: Output file exists: %s" % output_file)

    # TODO: Figure out how to check output directory permissions
    # elif not os.access(dirname(output_file), os.W_OK):
    #     bail = True
    #     vprint("ERROR: Need write access: %s" % dirname(output_file))

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prep input and output OGR objects
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Open grid file
    grid_ds = ogr.Open(grid_file)
    if grid_ds is None:
        bail = True
        vprint("ERROR: Could not open grid file: %s" % grid_file)

    # Open region file
    region_ds = ogr.Open(region_file)
    if region_ds is None:
        bail = True
        vprint("ERROR: Could not open region file: %s" % region_file)

    # Get output driver and output datasource
    output_ds = None
    output_driver = ogr.GetDriverByName(output_driver_name)
    if output_driver is None:
        bail = True
        vprint("ERROR: Invalid output driver: %s" % output_driver_name)
    elif not output_driver.TestCapability('CreateDataSource'):
        bail = True
        vprint("ERROR: Output driver does not support datasource creation: %s" % output_driver_name)
    else:
        output_ds = output_driver.CreateDataSource(output_file, options=output_dsco)
        if output_ds is None:
            bail = True
            vprint("ERROR: Couldn't create output datasource: %s" % output_file)

        # Make sure output datasource can create layers
        if not output_ds.TestCapability('CreateLayer'):
            bail = True
            vprint("ERROR: Output driver does not support layer creation: %s" % output_driver_name)

    # Get grid layers to process
    all_grid_layers = None
    try:
        if grid_layer_name is None:
            all_grid_layers = [grid_ds.GetLayer(i) for i in range(grid_ds.GetLayerCount())]
        else:
            all_grid_layers = [grid_ds.GetLayerByName(i) for i in grid_layer_name.split(',')]
    except RuntimeError:
        bail = True
        vprint("ERROR: Invalid grid layer(s): %s" % grid_layer_name)

    # Get region layers to process
    all_region_layers = None
    try:
        if region_layer_name is None:
            all_region_layers = [region_ds.GetLayerByIndex(0)]
        else:
            all_region_layers = [region_ds.GetLayerByName(i) for i in region_layer_name.split(',')]
    except RuntimeError:
        bail = True
        vprint("ERROR: Invalid region layer(s): %s" % region_layer_name)

    # Make sure all region layers are polygon or multipolygon (or 25D variants)
    for region_layer in all_region_layers:
        if region_layer.GetGeomType() not in (ogr.wkbPolygon, ogr.wkbPolygon25D,
                                              ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D):
            bail = True
            vprint("ERROR: Region layer '%s' is not a multi/polygon/25D" % region_layer.GetName())

    # Make sure all grid layers are polygon or multipolygon (or 25D variants)
    for grid_layer in all_grid_layers:
        if grid_layer.GetGeomType() not in (ogr.wkbPolygon, ogr.wkbPolygon25D,
                                            ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D):
            bail = True
            vprint("ERROR: Grid layer '%s' is not a multi/polygon/25D" % grid_layer.GetName())

    # Encountered an error - close everything and exit
    if bail:
        region_layer = None
        grid_layer = None
        output_driver = None
        output_ds = None
        all_region_layers = None
        all_grid_layers = None
        grid_ds = None
        region_ds = None
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prepare input data
    #/* ----------------------------------------------------------------------- */#

    # Process every combination of region layer and grid layer
    region_layer_counter = 0
    grid_layer_counter = 0
    for region_layer in all_region_layers:

        # Update user
        region_layer_counter += 1
        vprint("Processing region layer %s/%s: %s" % (region_layer_counter, len(all_region_layers),
                                                      region_layer.GetName()))

        for grid_layer in all_grid_layers:

            # Get field definitions for processing
            # Make sure there are no duplicate fields

            # Get feature definitions
            region_feature_def = region_layer.GetLayerDefn()
            grid_feature_def = grid_layer.GetLayerDefn()

            # Get field definitions
            region_field_definitions = [region_feature_def.GetFieldDefn(i) for i in range(region_feature_def.GetFieldCount())]
            grid_field_definitions = [grid_feature_def.GetFieldDefn(i) for i in range(grid_feature_def.GetFieldCount())]

            # Get list of fields - used to check for duplicate fields and used to populate output features
            region_layer_fields = [i.GetName() for i in region_field_definitions]
            grid_layer_fields = [i.GetName() for i in grid_field_definitions]

            # Check for duplicate fields
            bail = False
            for r_field in region_layer_fields:
                if r_field in grid_layer_fields:
                    bail = True
                    vprint("ERROR: Duplicate field: %s" % r_field)
            if bail:
                r_field = None
                region_feature_def = None
                grid_feature_def = None
                region_field_definitions = None
                grid_field_definitions = None
                grid_layer = None
                region_layer = None
                return 1

            # Update user
            grid_layer_counter += 1
            vprint("  Processing grid layer %s/%s: %s" % (grid_layer_counter, len(all_grid_layers), grid_layer.GetName()))

            # Create output layer
            output_layer_name = region_layer.GetName() + '-' + grid_layer.GetName()
            output_layer = output_ds.CreateLayer(output_layer_name, srs=grid_layer.GetSpatialRef(),
                                                 geom_type=ogr.wkbMultiPolygon, options=output_lco)
            for field_def in region_field_definitions + grid_field_definitions:
                output_layer.CreateField(field_def)

            # Cleanup
            region_field_definitions = None
            grid_field_definitions = None
            region_feature_def = None
            grid_feature_def = None
            field_def = None

            # Cache SRS objects
            grid_layer_srs = region_layer.GetSpatialRef()
            region_layer_srs = region_layer.GetSpatialRef()

            # Create a coordinate transformation object if the region_layer and grid_layer are in a different SRS
            if grid_layer_srs.IsSame(region_layer_srs) is not 1:
                coord_transform = osr.CoordinateTransformation(region_layer_srs, grid_layer_srs)
            else:
                coord_transform = None

            #/* ----------------------------------------------------------------------- */#
            #/*     Process data
            #/* ----------------------------------------------------------------------- */#


            # Create an initial spatial filter consisting of one convex hull for every input region
            # This yields a much smaller set of grid tiles that need to be examined
            # Dump these filtered grid cells into an in-memory layer
            # Loop through all regions, set a spatial filter on the in-memory layer = convex hull
            # Stamp out all grid cells

            vprint("    Progress units are region features")
            vprint("    Prepping data ...")

            # Create an initial spatial filter from all input geometries
            # Create a single geometry containing one convex hull for every input feature
            limit_geom = ogr.Geometry(ogr.wkbGeometryCollection)
            limit_geom.AssignSpatialReference(region_layer.GetSpatialRef())
            for region_feature in region_layer:
                region_geom = region_feature.GetGeometryRef()
                limit_geom.AddGeometry(region_geom.ConvexHull())
            if limit_geom.GetSpatialReference().IsSame(grid_layer_srs) is not 1:
                limit_geom.Transform(coord_transform)
            region_layer.ResetReading()
            grid_layer.SetSpatialFilter(limit_geom)
            region_feature = None
            region_geom = None

            # Stash all the found grid cells into an in memory layer
            mem_driver = ogr.GetDriverByName('Memory')
            mem_ds = mem_driver.CreateDataSource('mem_grids')
            mem_layer = mem_ds.CreateLayer('mem_grids', grid_layer.GetSpatialRef(), grid_layer.GetGeomType())
            for grid_feature in grid_layer:
                mem_layer.CreateFeature(grid_feature)
            grid_layer.ResetReading()

            # Loop through the region polygons, set a spatial filter
            region_feature_counter = 0
            num_region_features = len(region_layer)
            fid_counter = -1
            for region_feature in region_layer:

                # Update user
                region_feature_counter += 1
                sys.stdout.write("\r\x1b[K" + "    %s/%s" % (region_feature_counter, num_region_features))
                sys.stdout.flush()

                region_geom = region_feature.GetGeometryRef().Clone()
                if coord_transform is not None:
                    region_geom.Transform(coord_transform)
                mem_layer.ResetReading()
                mem_layer.SetSpatialFilter(region_geom.ConvexHull())

                # Stamp out all intersecting grids and add to output layer
                for m_grid_feature in mem_layer:

                    m_grid_geom = m_grid_feature.GetGeometryRef()
                    intersecting_geom = m_grid_geom.Intersection(region_geom)
                    output_geom = ogr.Geometry(ogr.wkbMultiPolygon)

                    # NOTE: This logic ONLY allows multi/polygons to pass through - although first IF statement might let others through
                    # Logic in the validate section still only allows polygons

                    # Intersecting geometry contains a polygon and may be immediately added to the output
                    if intersecting_geom.GetGeometryType() in (ogr.wkbPolygon, ogr.wkbPolygon25D):
                        output_geom.AddGeometry(intersecting_geom)
                        intersecting_geom = None

                    # Intersecting geometry is a linearring that is actually a closed polygon
                    # Convert to a polygon and add
                    elif intersecting_geom.GetGeometryType() is ogr.wkbLinearRing and is_ring_poly(intersecting_geom):
                        output_geom.AddGeometry(ring2poly(intersecting_geom))
                        intersecting_geom = None

                    # Intersecting geometry is a multipolygon - split into and add individual polygons
                    elif intersecting_geom.GetGeometryType() in (ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D):
                        for add_poly in [intersecting_geom.GetGeometryRef(i) for i in range(intersecting_geom.GetGeometryCount())]:
                            output_geom.AddGeometry(add_poly)
                        add_poly = None
                        intersecting_geom = None

                    # Intersecting geometry contains only a single point and may be discarded
                    elif intersecting_geom.GetGeometryCount() is 0 and intersecting_geom.GetPointCount() is 1:
                        intersecting_geom = None

                    # Intersecting geometry contains a linestring or multilinestring and can be discarded
                    elif intersecting_geom.GetGeometryType() in (ogr.wkbLineString, ogr.wkbLineString25D,
                                                                 ogr.wkbMultiLineString, ogr.wkbMultiLineString25D):
                        intersecting_geom = None

                    # The edge cases of edge cases - the "gridify problem"
                    # Geometry collection could contain any combination of points, multipoints, lines, multilines,
                    # linearrings, polygons, and multipolygons.  All must be dealt with.
                    elif intersecting_geom.GetGeometryType() is ogr.wkbGeometryCollection:
                        for sub_geom_i in range(intersecting_geom.GetPointCount()):
                            sub_geom = intersecting_geom.GetGeometryRef(sub_geom_i)

                            # Sub geometry is a polygon - add to output
                            if sub_geom.GetGeometryType() in (ogr.wkbPolygon, ogr.wkbPolygon25D):
                                output_geom.AddGeometry(sub_geom)

                            # Sub geometry is a linearring that is actually a closed and should be a polygon
                            elif sub_geom.GetGeometryType() is ogr.wkbLinearRing and is_ring_poly(sub_geom):
                                output_geom.AddGeometry(ring2poly(sub_geom))

                            # Sub geometry is a multipolygon - explode and add individually
                            elif sub_geom.GetGeometryType() in (ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D):
                                for add_poly in [sub_geom.GetGeometryRef(i) for i in range(sub_geom.GetGeometryCount())]:
                                    output_geom.AddGeometry(add_poly)
                                add_poly = None

                        sub_geom = None
                        intersecting_geom = None

                    # Unrecognized geometry type
                    else:
                        raise TypeError("Unhandled geometry type '%s' with name '%s' Grid FID: '%s' Region FID: '%s'"
                                        % (intersecting_geom.GetGeometryType(), intersecting_geom.GetGeometryName(),
                                           m_grid_feature.GetFID(), region_feature.GetFID()))

                    # Add output feature
                    if not output_geom.IsEmpty():
                        output_feature = region_feature.Clone()
                        fid_counter += 1
                        output_feature.SetFID(fid_counter)
                        output_feature.SetGeometry(output_geom)
                        output_layer.CreateFeature(output_feature)

            # Update user - done processing a grid layer
            vprint(" - Done")
            output_layer.SyncToDisk()

    # Cleanup
    sub_geom = None
    all_geoms = None
    output_geom = None
    bottom_geom = None
    temp_geom = None
    sub_geom = None
    m_grid_feature = None
    m_grid_geom = None
    mem_layer = None
    mem_ds = None
    mem_driver = None
    limit_geom = None
    coord_transform = None
    region_geom = None
    grid_geom = None
    intersecting_geom = None
    output_feature = None
    output_layer = None
    region_layer_srs = None
    grid_layer_srs = None
    region_layer = None
    grid_layer = None

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and final return
    #/* ----------------------------------------------------------------------- */#

    # Close OGR objects
    output_driver = None
    output_ds = None
    region_layers = None
    grid_layers = None
    grid_ds = None
    region_ds = None

    return 0


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Didn't get enough arguments - print usage and exit
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - give sys.argv[1:] to main()
    else:
        sys.exit(main(sys.argv[1:]))
