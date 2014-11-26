#!/usr/bin/env python


from __future__ import division
from __future__ import unicode_literals

import argparse
from os.path import basename
import sys


try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
gdal.UseExceptions()
ogr.UseExceptions()


# =========================================================================== #
#   Global variables
# =========================================================================== #

__version__ = '0.1-dev'
__program_name__ = basename(__file__)


# =========================================================================== #
#   Define main() function
# =========================================================================== #

def main(args):

    # --------------------------------------------------------------------------- #
    #   Parse arguments
    # --------------------------------------------------------------------------- #

    parser = argparse.ArgumentParser(
        prog=__program_name__,
    )

    # Help arguments
    parser.add_argument(
        '--help-info',
        dest='help_info',
        action='store_true',
        help='Display more detailed help information'
    )

    # Output options
    parser.add_argument(
        '-of', '--output-format',
        dest='driver_name',
        type=str,
        action='store',
        default='GTiff',
        metavar='driver',
        help='Output raster driver name'
    )
    parser.add_argument(
        '-tr', '--target-res',
        required=True,
        dest='target_resolution',
        type=int,
        nargs=2,
        action='store',
        metavar=('xres', 'yres'),
        help='Target pixel resolution in georeferenced units'
    )
    parser.add_argument(
        '-at', '--all-touched',
        dest='all_touched',
        action='store_true',
        default=False,
        help="Rasterizes features into all touched pixels instead of just those on the line render path or whose center point is within the polygon"
    )
    parser.add_argument(
        '-nd', '--nodata',
        dest='nodata',
        default=0,
        type=int,
        action='store',
        help='Destination nodata value'
    )
    parser.add_argument(
        '-md', '--max-distance',
        dest='max_distance',
        type=int,
        action='append',
        help='Maximum search distance for non-nodata pixels when computing distance'
    )
    parser.add_argument(
        '-du', '-dist-units',
        dest='distance_units',
        choices=('GEO', 'PIXEL'),
        default='GEO',
        type=str,
        action='store',
        help='Values to write when computing distance - num pixels or georeferenced units'
    )
    parser.add_argument(
        '-fbv', '--fixed-buff-val',
        dest='fixed_buffer_val',
        type=int,
        action='store',
        help='Write this value instead of distance for all pixels that are within the max distance'
    )
    parser.add_argument(
        '-l', '--layers',
        dest='layers_to_process',
        type=str,
        nargs='+',
        action='append',
        help='Layers to process'
    )
    parser.add_argument(
        '-co', '--creation-option',
        dest='creation_options',
        type=str,
        default=[],
        action='append',
        metavar='OPTION=VAL',
        help='Output format supported creation option'
    )
    parser.add_argument(
        '-ovr', '--overview',
        dest='overviews',
        type=int,
        nargs='+',
        metavar='level',
        help='Overview levels'
    )
    parser.add_argument(
        '-or', '--ovr-resampling',
        dest='overview_resampling',
        choices=('nearest', 'average', 'gauss', 'cubic', 'average_mp', 'average_magphase', 'mode'),
        default='nearest',
        help='Overview resampling method'
    )
    parser.add_argument(
        '--overwrite',
        dest='overwrite_mode',
        action='store_true',
        default=False,
        help='Blindly overwrite the output file if it exists'
    )
    # Positional arguments and errors
    parser.add_argument(
        'input_vector',
        metavar='src_vector',
        type=str,
        action='store',
        help='Vector to calculate distance against'
    )
    parser.add_argument(
        'output_raster',
        metavar='dst_raster',
        type=str,
        action='store',
        help='Output raster containing distance values'
    )

    pargs = parser.parse_args(args=args)

    # --------------------------------------------------------------------------- #
    #   Adjust and validate parameters
    # --------------------------------------------------------------------------- #

    # Force cell sizes to be positive
    pargs.target_resolution = [abs(i) for i in pargs.target_resolution]

    bail = False

    # Check input vector
    try:
        ds = ogr.Open(pargs.input_vector, 0)
        if ds is None:
            del ds
            bail = True
            print("ERROR: Can't access input vector: %s" % pargs.input_vector)
    except RuntimeError:
        pass

    # Check output raster
    try:
        ds = gdal.Open(pargs.output_raster, 0)
        if ds is not None and not pargs.overwrite_mode:
            ds = None
            bail = True
            print("ERROR: Overwrite=%s and output raster exists: %s" % (pargs.overwrite_mode, pargs.output_raster))
    except RuntimeError:
        pass

    if bail:
        return 1

    # --------------------------------------------------------------------------- #
    #   Prep workspace
    # --------------------------------------------------------------------------- #

    vds = ogr.Open(pargs.input_vector)

    # Get full extent of all vector layers being processed and make sure all layers are in the same spatial reference
    print("Computing input vector extent ...")
    vds_srs = None
    vds_extent = []
    for layer in vds:
        if pargs.layers_to_process is None or layer.GetName() in pargs.layers_to_process:

            # Check SRS
            if vds_srs is None:
                vds_srs = layer.GetSpatialRef()
            elif not vds_srs.IsSame(layer.GetSpatialRef()):
                vds = None
                print("ERROR: One or more input layers do not have the same SRS")
                return 1

            # Update extent
            min_x, max_x, min_y, max_y = layer.GetExtent()
            if len(vds_extent) is 0:
                vds_extent = [min_x, min_y, max_x, max_y]
            else:
                if min_x < vds_extent[0]:
                    vds_extent[0] = min_x
                if min_y < vds_extent[1]:
                    vds_extent[1] = min_y
                if max_x > vds_extent[2]:
                    vds_extent[2] = max_x
                if max_y > vds_extent[3]:
                    vds_extent[3] = max_y

    # Construct an in-memory raster that will store the rasterized vectors
    print("Building an in-memory raster for rasterization ...")
    vds_geotransform = (vds_extent[0], pargs.target_resolution[0], 0, vds_extent[3], 0, -pargs.target_resolution[1])
    x_res = int((vds_extent[2] - vds_extent[0]) / pargs.target_resolution[0])
    y_res = int((vds_extent[3] - vds_extent[1]) / pargs.target_resolution[1])
    rize_ds = gdal.GetDriverByName(str('MEM')).Create(str('rasterization_memory_ds'), x_res, y_res, 1, gdal.GDT_Byte)
    rize_ds.SetGeoTransform(vds_geotransform)
    rize_ds.SetProjection(vds_srs.ExportToWkt())
    band = rize_ds.GetRasterBand(1)
    band.SetNoDataValue(pargs.nodata)
    band = None

    # Create output datasource
    rdriver = gdal.GetDriverByName(str(pargs.driver_name))
    if rdriver is None:
        vds = None
        rize_ds = None
        print("ERROR: Invalid driver: '%s'" % pargs.driver_name)
        return 1
    rds = rdriver.Create(
        str(pargs.output_raster), rize_ds.RasterXSize, rize_ds.RasterYSize, 1, gdal.GDT_Float32,
        options=pargs.creation_options
    )
    if rds is None:
        vds = None
        rize_ds = None
        print("ERROR: Could not create output raster: %s" % pargs.output_raster)
        return 1
    rdriver = None


    rds.SetGeoTransform(vds_geotransform)
    rds.SetProjection(vds_srs.ExportToWkt())

    # --------------------------------------------------------------------------- #
    #   Rasterize input layers
    # --------------------------------------------------------------------------- #

    if pargs.all_touched:
        rize_options = ['ALL_TOUCHED=TRUE']
    else:
        rize_options = []
    rize_options.append('MERGE_ALG=REPLACE')
    rize_options = [str(opt) for opt in rize_options]
    for layer in vds:
        if pargs.layers_to_process is None or layer.GetName() in pargs.layers_to_process:
            print("Rasterizing layer '%s' ..." % layer.GetName())
            gdal.RasterizeLayer(rize_ds, [1], layer, options=rize_options, burn_values=[1], callback=gdal.TermProgress)

    # --------------------------------------------------------------------------- #
    #   Compute proximity
    # --------------------------------------------------------------------------- #

    # Assemble options for proximity calculation
    proximity_options = []
    if pargs.max_distance:
        proximity_options.append('MAXDIST=%s' % pargs.max_distance)
    if pargs.distance_units:
        proximity_options.append('DISTUNITS=%s' % pargs.distance_units)
    if pargs.fixed_buffer_val:
        proximity_options.append('FIXED_BUF_VAL=%s' % pargs.fixed_buffer_val)
    proximity_options.append('VALUES=1')
    proximity_options.append('NODATA=0')
    proximity_options = [str(opt) for opt in proximity_options]

    # Compute proximity
    print("Computing proximity ...")
    output_band = rds.GetRasterBand(1)
    output_band.SetNoDataValue(pargs.nodata)
    gdal.ComputeProximity(rize_ds.GetRasterBand(1), output_band, options=proximity_options, callback=gdal.TermProgress)

    # --------------------------------------------------------------------------- #
    #   Generate overviews
    # --------------------------------------------------------------------------- #

    if pargs.overviews:
        print("Generating overview: %s" % ', '.join([str(o) for o in pargs.overviews]))
        rds.BuildOverviews(resampling=str(pargs.overview_resampling), overviewlist=pargs.overviews, callback=gdal.TermProgress)

    # Cleanup
    band = None
    output_band = None
    vds_srs = None
    vds = None
    layer = None
    rize_ds = None
    rds = None

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
