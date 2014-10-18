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


"""Pelagos Regionate

Usage:
  regionate.py [options] POLY_LAYER [POINTS_IN [POINTS_OUT]] [-q | -v]
  regionate.py [options] POLY_LAYER [-] [POINTS_OUT] [-q | -v]
  regionate.py (-h | --help)
  regionate.py --version

Options:
  --attribute=ATTRIB    Attribute in the polygon layer containing the regionid [default: regionid]
  --layername=LAYERNAME     Name of the polygon layer to use.  Default is to use the all layers
  --xfield=XFIELD       Name of input field containing x value [default: longitude]
  --yfield=YFIELD       Name of input field containing x value [default: latitude]
  --regionid-map=DEFINITION    LAYER=FIELD,FIELD,...:LAYER=FIELD:...
  --regionid-mode=MODE  (update|append) Specify whether regionid's should be appended or updated [default: append]
  -h --help     Show this screen.
  --version     Show version.
  -q --quiet    be quiet
  -v --verbose  yak yak yak
"""


from docopt import docopt

import logging
import csv
import sys
import json
from osgeo import ogr


#/* ======================================================================= */#
#/*     Define load_layers() function
#/* ======================================================================= */#

def load_layers(data_source, arg):

    """
    Load specified layers
    """

    layers = []
    layer_name = arg['--layername']
    for i in range(0, data_source.GetLayerCount()):
        layer = data_source.GetLayerByIndex(i)
        if layer_name:
            if layer_name == layer.GetName():
                layers.append(layer)
        else:
            if layer.GetGeomType() in (3, 6):
                layers.append(layer)
    if not layers:
        if arg['--layername']:
            raise IOError('Layer %s not found in %s' % (arg['--layername'], arg['POLY_LAYER']))
        else:
            raise IOError('No Polygon layers found in %s' % arg['POLY_LAYER'])

    return layers


#/* ======================================================================= */#
#/*     Define regionate() function
#/* ======================================================================= */#

def regionate(file_in, file_out, arg):

    """
    Open polygon layer for reading
    Arguments are file path and layer name
    Unfortunately a layer cannot exist without an open datasource so both objects must exist
    poly_ds, poly_layer = putils.io.open_datasource(arg['POLY_LAYER'], basename(arg['POLY_LAYER']).split('.')[0])
    """

    # Prep OGR objects
    poly_ds = ogr.Open(arg['POLY_LAYER'], 0)
    if poly_ds is None:
        raise IOError('Unable to open %s' % arg['POLY_LAYER'])
    layers = load_layers(poly_ds, arg)

    regionid_map = {layer.GetName(): ['region'] for layer in layers}

    if arg['--regionid-map'] is not None:

        # Parse the region map definitions
        definitions = arg['--regionid-map'].split(':')
        for defn in definitions:
            layer, fields = defn.split('=')
            regionid_map[layer] = fields.split(',')

    # Extract all the fields specified in the region map so they can be created if they do not already exist
    regionid_fields = []
    for r_fields in regionid_map.values():
        regionid_fields += r_fields

    # Prep CSV objects
    reader = csv.DictReader(file_in)

    # Process one row at a time
    for row in reader:
        point = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (row['longitude'], row['latitude']))
        regionids = {}

        # Perform point in polygon tests for all layers
        for layer in layers:
            layer.SetSpatialFilter(point)
            feature = layer.GetNextFeature()

            # Check all intersecting features for current layer
            while feature:

                if feature.GetGeometryRef().Intersects(point):
                    value = feature.GetField(arg['--attribute'])
                    if value is not None:
                        value = value.split(',')

                        # Add regionid
                        if layer.GetName() not in regionids:
                            regionids[layer.GetName()] = value
                        else:
                            regionids[layer.GetName()] += value

                feature = layer.GetNextFeature()

        # Create an output row
        row_out = row.copy()

        # # No regionid mapping - populate
        # if regionid_map is None:
        #     _ids = []
        #     for _rids in regionids.values():
        #         _ids += _rids
        #     row_out['region'] = _ids
        #
        # # Regionids are mapped to multiple fields, distribute
        # else:

        # Make sure output row contains all necessary fields
        for rid_field in regionid_fields:
            if rid_field not in row_out:
                row_out[rid_field] = []

        # Populate output regionid's
        for layer_name, collected_ids in regionids.iteritems():
            for ofield in regionid_map[layer_name]:

                # If the field is empty, set it equal to the collected regionids
                # If the field should be updated, replace existing values with new
                if row_out[ofield] is None or arg['--regionid-mode'] == 'update':
                    row_out[ofield] = regionids[layer_name]

                # Add to existing values
                elif arg['--regionid-mode'] == 'append':
                    row_out[ofield] += regionids[layer_name]

                # Argument error
                else:
                    raise ValueError("Invalid --regionid-mode: %s" % arg['--regionid-mode'])

        # Dump to disk

        # HACK for special "ocean" field.  Need to make a way in the regionid-map definition that you can
        # specify whether the field is output as a list or as a string

        row_out['ocean'] = ','.join(row_out.get('ocean',[]))

        file_out.write(json.dumps(row_out, sort_keys=True))
        file_out.write('\n')


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main():

    # Parse arguments
    arguments = docopt(__doc__, version='Pelagos Regionator 0.1')
    if arguments['--verbose']:
        log_level = logging.DEBUG
    elif arguments.get('--quiet'):
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    try:
        points_in = arguments['POINTS_IN']
        points_out = arguments['POINTS_OUT']

        # Open input file
        with sys.stdin if points_in is None or '-' == points_in else open(points_in, 'rb') as file_in:

            # Open output file
            with sys.stdout if points_out is None or '-' == points_out else open(points_out, 'w') as file_out:
                regionate(file_in, file_out, arguments)

    except (ValueError, IOError), e:
        logging.error(e)
        return 1

    return 0


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == "__main__":

    sys.exit(main())
