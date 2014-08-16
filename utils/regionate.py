#!/usr/bin/env python
"""Pelagos Model Transform.

Usage:
  process_ais.py [options] POLY_LAYER [POINTS_IN [POINTS_OUT]] [-q | -v]
  process_ais.py [options] POLY_LAYER [-] [POINTS_OUT] [-q | -v]
  process_ais.py (-h | --help)
  process_ais.py --version

Options:
  --attribute=ATTRIB   Attribute in the polygon layer containing the regionid [default: regionid]
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
from os.path import *

import putils

def transform (arg):

    points_in=arg['POINTS_IN']
    points_out=arg['POINTS_OUT']

    # Open polygon layer for reading
    # Arguments are file path and layer name
    # Unfortunately a layer cannot exist without an open datasource so both objects must exist
    poly_ds, poly_layer = putils.io.open_datasource(arg['POLY_LAYER'], basename(arg['POLY_LAYER']).split('.')[0])

    with sys.stdin if points_in is None or '-' == points_in else open(points_in, 'rb') as file_in:
        with sys.stdout if points_out is None or '-' == points_out else open(points_out, 'w') as file_out:
            reader = csv.DictReader(file_in)
            fieldnames = reader.fieldnames
            for row in reader:
                regions = putils.classify.get_all_intersecting_attributes(row[arg['--xfield']],
                                                                          row[arg['--yfield']],
                                                                          poly_layer)

                regionids = [r.get(arg['--attribute']) for r in regions.values()]
                row_out = row
                row_out['region'] = regionids
                file_out.write(json.dumps(row_out))
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
        transform(arguments)
    except (ValueError, IOError), e:
        logging.error(e)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
