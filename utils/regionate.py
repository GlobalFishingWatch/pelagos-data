#!/usr/bin/env python
"""Pelagos Regionate

Usage:
  regionate.py [options] POLY_LAYER [POINTS_IN [POINTS_OUT]] [-q | -v]
  regionate.py [options] POLY_LAYER [-] [POINTS_OUT] [-q | -v]
  regionate.py (-h | --help)
  regionate.py --version

Options:
  --attribute=ATTRIB   Attribute in the polygon layer containing the regionid [default: regionid]
  --layername=LAYERNAME   Name of the polygon layer to use.  Default is to use the first layer found
  --xfield=XFIELD      Name of input field containing x value [default: longitude]
  --yfield=YFIELD      Name of input field containing x value [default: latitude]
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


# def load_layer(file_name, layer_name=None):
#     poly_ds = ogr.Open(file_name, 0)
#     if poly_ds is None:
#         raise IOError('Unable to open %s' % file_name)
#
#     # if layer_name:
#     #     print file_name, layer_name
#     #     layer = poly_ds.GetLayerByName('ocean2')
#     #     if layer:
#     #         return layer
#     #     else:
#     #         raise IOError('Layer %s not found in %s' % (layer_name, file_name))
#
#     # get all layers that are polyon (3) or multipolygon(6)
#     for i in range(0,poly_ds.GetLayerCount()):
#         # only use the first usable layer
#
#         layer = poly_ds.GetLayerByIndex(i)
#         if layer_name:
#             if layer.GetName() == layer_name:
#                 return layer
#         else:
#             if layer.GetGeomType() in (3,6):
#                 return layer
#
#     if layer_name:
#         raise IOError('Layer %s not found in %s' % (layer_name, file_name))
#     else:
#         raise IOError('No Polygon layers found in %s' % file_name)
def load_layers (data_source, arg):
    layers = []
    layer_name = arg['--layername']
    for i in range(0,data_source.GetLayerCount()):
        layer = data_source.GetLayerByIndex(i)
        if layer_name:
            if layer_name == layer.GetName():
                layers.append(layer)
        else:
            if layer.GetGeomType() in (3,6):
                layers.append(layer)

    if not layers:
        if arg['--layername']:
            raise IOError('Layer %s not found in %s' % (arg['--layername'], arg['POLY_LAYER']))
        else:
            raise IOError('No Polygon layers found in %s' % arg['POLY_LAYER'])

    return layers

def regionate (file_in, file_out, arg):

    # Open polygon layer for reading
    # Arguments are file path and layer name
    # Unfortunately a layer cannot exist without an open datasource so both objects must exist
    # poly_ds, poly_layer = putils.io.open_datasource(arg['POLY_LAYER'], basename(arg['POLY_LAYER']).split('.')[0])

    poly_ds = ogr.Open(arg['POLY_LAYER'], 0)
    if poly_ds is None:
        raise IOError('Unable to open %s' % arg['POLY_LAYER'])

    layers = load_layers(poly_ds, arg)

    reader = csv.DictReader(file_in)
    fieldnames = reader.fieldnames
    for row in reader:
        point = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (row['longitude'], row['latitude']))
        regionids = []
        for layer in layers:
            layer.SetSpatialFilter(point)
            feature = layer.GetNextFeature()
            while feature:
                field_idx = feature.GetFieldIndex(arg['--attribute'])
                if field_idx != -1 and feature.GetGeometryRef().Intersects(point):
                    regionids += feature.GetFieldAsString(field_idx).split(',')
                feature = layer.GetNextFeature()
        row_out = row
        row_out['region'] = regionids
        file_out.write(json.dumps(row_out, sort_keys=True))
        file_out.write('\n')


def main():
    arguments = docopt(__doc__, version='Pelagos Regionator 0.1')

    if arguments['--verbose']:
        log_level = logging.DEBUG
    elif arguments.get('--quiet'):
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    try:
        points_in=arguments['POINTS_IN']
        points_out=arguments['POINTS_OUT']

        with sys.stdin if points_in is None or '-' == points_in else open(points_in, 'rb') as file_in:
            with sys.stdout if points_out is None or '-' == points_out else open(points_out, 'w') as file_out:
                regionate(file_in ,file_out, arguments)
    except (ValueError, IOError), e:
        logging.error(e)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
