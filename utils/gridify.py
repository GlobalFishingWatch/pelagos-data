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

# TODO: Populate docstring
"""
Clip arbitrary regions to quad tree levels
"""


import multiprocessing
import os
from os.path import *
import sys

try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr
ogr.UseExceptions()
osr.UseExceptions()


#/* ======================================================================= */#
#/*     Build information
#/* ======================================================================= */#

__version__ = '0.1-dev'
__release__ = 'August 28, 2014'
__author__ = 'Kevin D. Wurster'
__source__ = 'https://github.com/SkyTruth/pelagos-data'
__docname__ = basename(__file__)
__license__ = '''
The MIT License (MIT)

Copyright (c) 2014 SkyTruth

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


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
    print("""
Usage:
    {0} [-of ogr_driver] [-lco option=value] [-dsco option=value]
    {1} [-gl layer_name|layer1,layer2,...] [-rl layer_name|layer1,layer2]
    {1} --grid=grid_file.ext --region=region_file.ext -o output_file.ext
""".format(__docname__, " " * len(__docname__)))
    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print out license information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print(__license__)

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
    print("""
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

    print("""
Help flags:
    --help      More detailed description of this utility
    --usage     Arguments, parameters, flags, options, etc.
    --version   Version and ownership information
    --license   License information
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_version():

    """
    Print script version information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
%s version %s - released %s
    """ % (__docname__, __version__, __release__))

    return 1


def process_layers(grid_layer, region_layer, coord_transform):

    pass


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    output_driver_name = "ESRI Shapefile"
    processing_algorithm = 'combined'

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    options_processing_algorithm = ('region', 'grid', 'combined', 'regionnohull')
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
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info'):
                return print_help_info()
            elif arg in ('--help', '-help', '--h', '-h'):
                return print_help()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--license', '-usage'):
                return print_license()

            # Specify input files
            elif '--grid=' in arg:
                i += 1
                grid_file = arg.split('=', 1)[1]
            elif '-gl' in arg:
                i += 2
                grid_layer_name = args[i - 1]
            elif '--region=' in arg:
                i += 1
                region_file = arg.split('=', 1)[1]
            elif '-rl' in arg:
                i += 1
                region_layer_name = args[i - 1]

            # Output file
            elif arg == '-o':
                i += 2
                output_file = args[i - 1]

            # OGR output options
            elif arg == '-of':
                i += 2
                output_driver_name = args[i - 1]
            elif arg == '-lco':
                i += 2
                output_lco.append(args[i - 1])
            elif arg == '-dsco':
                i += 2
                output_dsco.append(args[i - 1])

            # Additional options
            elif '--algorithm=' in arg:
                i += 1
                processing_algorithm = args[i - 1].split('=', 1)[1]

            # Positional arguments and errors
            else:

                # Invalid argument
                i += 1
                arg_error = True
                print("ERROR: Invalid argument: %s" % arg)

        # This catches several conditions:
        #   1. The last argument is a flag that requires parameters but the user did not supply the parameter
        #   2. The arg parser did not properly consume all parameters for an argument
        #   3. The arg parser did not properly iterate the 'i' variable
        #   4. An argument split on '=' doesn't have anything after '=' - e.g. '--output-file='
        except (IndexError, ValueError):
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters: %s" % arg)

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate parameters
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check input driver name
    if not isinstance(output_driver_name, str):
        bail = True
        print("ERROR: Invalid output driver name: %s" % output_driver_name)

    # Check input grid file
    if not isinstance(grid_file, str):
        bail = True
        print("ERROR: Invalid input grid file: %s" % grid_file)
    elif not os.access(grid_file, os.R_OK):
        bail = True
        print("ERROR: Invalid input grid file: %s" % grid_file)

    # Check input region file
    if not isinstance(region_file, str):
        bail = True
        print("ERROR: Invalid input region file: %s" % region_file)
    elif not os.access(region_file, os.R_OK):
        bail = True
        print("ERROR: Can't access input region file: %s" % region_file)

    # Check output file
    if not isinstance(output_file, str):
        bail = True
        print("ERROR: Invalid output file: %s" % output_file)
    elif os.path.exists(output_file):
        bail = True
        print("ERROR: Output file exists: %s" % output_file)
    # elif not os.access(dirname(output_file), os.W_OK):
    #     bail = True
    #     print("ERROR: Need write access: %s" % dirname(output_file))

    # Check additional options
    if processing_algorithm.lower() not in options_processing_algorithm:
        bail = True
        print("ERROR: Invalid processing algorithm: %s" % processing_algorithm)
        print("       Options: %s" % ', '.join(options_processing_algorithm))

    # Exit if something did not pass validation
    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prep input and output OGR objects
    #/* ----------------------------------------------------------------------- */#

    # Open grid file
    bail = False
    grid_ds = ogr.Open(grid_file)
    if grid_ds is None:
        bail = True
        print("ERROR: Could not open grid file: %s" % grid_file)

    # Open region file
    region_ds = ogr.Open(region_file)
    if region_ds is None:
        bail = True
        print("ERROR: Could not open region file: %s" % region_file)

    # Get output driver and output datasource
    output_ds = None
    output_driver = ogr.GetDriverByName(output_driver_name)
    if output_driver is None:
        bail = True
        print("ERROR: Invalid output driver: %s" % output_driver_name)
    elif not output_driver.TestCapability('CreateDataSource'):
        bail = True
        print("ERROR: Output driver does not support datasource creation: %s" % output_driver_name)
    else:
        output_ds = output_driver.CreateDataSource(output_file, options=output_dsco)
        if output_ds is None:
            bail = True
            print("ERROR: Couldn't create output datasource: %s" % output_file)

        # Make sure output datasource can create layers
        if not output_ds.TestCapability('CreateLayer'):
            bail = True
            print("ERROR: Output driver does not support layer creation: %s" % output_driver_name)

    # Get grid layers to process
    all_grid_layers = None
    try:
        if grid_layer_name is None:
            all_grid_layers = [grid_ds.GetLayer(i) for i in range(grid_ds.GetLayerCount())]
        else:
            all_grid_layers = [grid_ds.GetLayerByName(i) for i in grid_layer_name.split(',')]
    except RuntimeError:
        bail = True
        print("ERROR: Invalid grid layer(s): %s" % grid_layer_name)

    # Get region layers to process
    all_region_layers = None
    try:
        if region_layer_name is None:
            all_region_layers = [region_ds.GetLayerByIndex(0)]
        else:
            all_region_layers = [region_ds.GetLayerByName(i) for i in region_layer_name.split(',')]
    except RuntimeError:
        bail = True
        print("ERROR: Invalid region layer(s): %s" % region_layer_name)

    # Encountered an error - exit but close everything first
    if bail:
        output_driver = None
        output_ds = None
        all_region_layers = None
        all_grid_layers = None
        grid_ds = None
        region_ds = None
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Process data
    #/* ----------------------------------------------------------------------- */#

    # Process every combination of region layer and grid layer
    region_layer_counter = 0
    grid_layer_counter = 0
    for region_layer in all_region_layers:

        # Update user
        region_layer_counter += 1
        print("Processing region layer %s/%s: %s" % (region_layer_counter, len(all_region_layers),
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
                    print("ERROR: Duplicate field: %s" % r_field)
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
            print("  Processing grid layer %s/%s: %s" % (grid_layer_counter, len(all_grid_layers), grid_layer.GetName()))

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

            # TODO: Determine which algorithm to use - grid centric or region polygon centric

            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#
            #/*     Region polygon centric algorithm
            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#

            print("    Using algorithm: %s" % processing_algorithm)
            
            if processing_algorithm.lower() == 'region':

                # No upfront data prep
                # Uses the convex hull of the region feature being processed as a spatial index on every pass
                # Limits the number of grid cells being examined
                                
                # # Create an output chunk for every intersecting geometry for grid cell
                region_feature_counter = 0
                num_region_features = len(region_layer)
                region_layer.ResetReading()
                for region_feature in region_layer:
    
                    # Cache region geometry
                    region_geom = region_feature.GetGeometryRef().Clone()
                    if coord_transform is not None:
                        region_geom.Transform(coord_transform)
    
                    # Apply a spatial filter to the grid
                    spat_filter_geom = region_geom.ConvexHull()
                    grid_layer.SetSpatialFilter(spat_filter_geom)
                    grid_layer.ResetReading()

                    # Update user
                    region_feature_counter += 1
                    sys.stdout.write("\r\x1b[K" + "    %s/%s" % (region_feature_counter, num_region_features))
                    sys.stdout.flush()

                    for grid_feature in grid_layer:
    
                        grid_geom = grid_feature.GetGeometryRef()
    
                        intersecting_geom = grid_geom.Intersection(region_geom)
                        if not intersecting_geom.IsEmpty():
                            if intersecting_geom.GetGeometryType() is ogr.wkbGeometryCollection:
                                temp_geom = ogr.Geometry(ogr.wkbMultiPolygon)
                                for i in range(intersecting_geom.GetGeometryCount()):
                                    sub_geom = intersecting_geom.GetGeometryRef(i)
                                    if sub_geom.GetPointCount() > 2:
                                        temp_geom.AddGeometry(sub_geom)
                                intersecting_geom = temp_geom
                            output_feature = region_feature.Clone()
                            output_feature.SetGeometry(intersecting_geom)
                            output_layer.CreateFeature(output_feature)
    
                # Update user - done processing a grid layer
                print(" - Done")
                output_layer.SyncToDisk()

            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#
            #/*     Region polygon centric algorithm - NO CONVEX HULL
            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#

            elif processing_algorithm.lower() == 'regionnohull':

                # Same as above but uses the more complex region geometry as the spatial filter instead of a convex hull

                # # Create an output chunk for every intersecting geometry for grid cell
                region_feature_counter = 0
                num_region_features = len(region_layer)
                region_layer.ResetReading()
                for region_feature in region_layer:

                    # Cache region geometry
                    region_geom = region_feature.GetGeometryRef().Clone()
                    if coord_transform is not None:
                        region_geom.Transform(coord_transform)

                    # Spatial filter
                    grid_layer.SetSpatialFilter(region_geom)
                    grid_layer.ResetReading()

                    # Update user
                    region_feature_counter += 1
                    sys.stdout.write("\r\x1b[K" + "    %s/%s" % (region_feature_counter, num_region_features))
                    sys.stdout.flush()

                    for grid_feature in grid_layer:

                        grid_geom = grid_feature.GetGeometryRef()

                        intersecting_geom = grid_geom.Intersection(region_geom)
                        if not intersecting_geom.IsEmpty():
                            if intersecting_geom.GetGeometryType() is ogr.wkbGeometryCollection:
                                temp_geom = ogr.Geometry(ogr.wkbMultiPolygon)
                                for i in range(intersecting_geom.GetGeometryCount()):
                                    sub_geom = intersecting_geom.GetGeometryRef(i)
                                    if sub_geom.GetPointCount() > 2:
                                        temp_geom.AddGeometry(sub_geom)
                                intersecting_geom = temp_geom
                            output_feature = region_feature.Clone()
                            output_feature.SetGeometry(intersecting_geom)
                            output_layer.CreateFeature(output_feature)

                # Update user - done processing a grid layer
                print(" - Done")
                output_layer.SyncToDisk()

            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#
            #/*     Grid centric algorithms
            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#

            elif processing_algorithm.lower() == 'grid':
                    
                # Limit the number of features in the grid_layer that will be processed
                # Create a geometry collection containing one convex hull per region geometry
                # Use this geometry as a spatial filter on the grid layer
                # Be sure to reset reading afterwards
                # Get one grid feature and stamp out all intersecting region polygons
                #   Repeat ...

                print("    Progress units are grid features")
                print("    Prepping data ...")
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
                
                # Create an output chunk for every intersecting geometry for grid cell
                grid_feature_counter = 0
                num_grid_features = len(grid_layer)
                for grid_feature in grid_layer:

                    # Prep region layer
                    grid_geom = grid_feature.GetGeometryRef()
                    region_layer.ResetReading()
                    region_layer.SetSpatialFilter(grid_geom)

                    # Update user
                    grid_feature_counter += 1
                    sys.stdout.write("\r\x1b[K" + "    %s/%s" % (grid_feature_counter, num_grid_features))
                    sys.stdout.flush()

                    for region_feature in region_layer:
                
                        # Compute the intersection
                        region_geom = region_feature.GetGeometryRef().Clone()
                        if coord_transform is not None:
                            region_geom.Transform(coord_transform)
                        intersecting_geom = grid_geom.Intersection(region_geom)
                
                        # Add new feature to the output layer
                        if not intersecting_geom.IsEmpty():
                            if intersecting_geom.GetGeometryType() is ogr.wkbGeometryCollection:
                                temp_geom = ogr.Geometry(ogr.wkbMultiPolygon)
                                for i in range(intersecting_geom.GetGeometryCount()):
                                    sub_geom = intersecting_geom.GetGeometryRef(i)
                                    if sub_geom.GetGeometryType() in (ogr.wkbPolygon, ogr.wkbMultiPolygon):
                                        temp_geom.AddGeometry(sub_geom)
                                intersecting_geom = temp_geom
                            output_feature = region_feature.Clone()
                            output_feature.SetGeometry(intersecting_geom)
                            output_layer.CreateFeature(output_feature)
                
                # Update user - done processing a grid layer
                print(" - Done")
                output_layer.SyncToDisk()

            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#
            #/*     Combined
            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#

            elif processing_algorithm == 'combined':

                # Create an initial spatial filter consisting of one convex hull for every input region
                # This yields a much smaller set of grid tiles that need to be examined
                # Dump these filtered grid cells into an in-memory layer
                # Loop through all regions, set a spatial filter on the in-memory layer = convex hull
                # Stamp out all grid cells

                print("    Progress units are region features")
                print("    Prepping data ...")

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
                        if not intersecting_geom.IsEmpty():
                            if intersecting_geom.GetGeometryType() is ogr.wkbGeometryCollection:
                                temp_geom = ogr.Geometry(ogr.wkbMultiPolygon)
                                for i in range(intersecting_geom.GetGeometryCount()):
                                    sub_geom = intersecting_geom.GetGeometryRef(i)
                                    if sub_geom.GetPointCount() > 2:
                                        temp_geom.AddGeometry(sub_geom)
                                intersecting_geom = temp_geom
                            output_feature = region_feature.Clone()
                            output_feature.SetGeometry(intersecting_geom)

                            # TODO: Why are output fields being populated when this is commented out???

                            # for i, field in enumerate(region_layer_fields):
                            #     value = region_feature.GetField(i)
                            #     output_feature.SetField(field, value)
                            # for i, field in enumerate(grid_layer_fields):
                            #     value = region_feature.GetField(i)
                            #     output_feature.SetField(field, value)
                            output_layer.CreateFeature(output_feature)

                # Update user - done processing a grid layer
                print(" - Done")
                output_layer.SyncToDisk()
            
            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#
            #/*     Bad algorithm
            #/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */#
            
            else:
                print("ERROR: Invalid processing algorithm: %s" % processing_algorithm)
                return 1

    # Cleanup
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
