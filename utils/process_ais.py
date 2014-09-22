#!/usr/bin/env python
"""Pelagos Model Transform.

Usage:
  process_ais.py [INFILE [OUTFILE]] [-q | -v]
  process_ais.py [-] [OUTFILE] [-q | -v]
  process_ais.py (-h | --help)
  process_ais.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  -q --quiet    be quiet
  -v --verbose  yak yak yak
"""

from docopt import docopt

import logging
import csv
import sys

from vectortile import TileBounds


MAX_ZOOM = 15
MIN_SCORE = -15.0
MAX_SCORE = 5.0
MAX_INTERVAL = 24 * 60 * 60  # 24 hours
TYPE_NORMAL = 0
TYPE_SEGMENT_START = 1
TYPE_SEGMENT_END = 2


class Transform(object):

    def __init__(self):
        self.prev_row = None
        self.stats = {}

    # def get_regions(self, latitude, longitude):
    #     return []

    def _increment_stat(self, stat):
        if stat in self.stats:
            self.stats[stat] += 1
        else:
            self.stats[stat] = 1

    def transform_row(self, row):
        """
        Transform a a row of data and return the new row.   This does an update in place, so the passed row is modified.
        If one of the fields contains an out of range value the function returns None and logs an error.
        """
        # skip rows with bad lat/lon values
        lat = float(row['latitude'])
        if lat > 90 or lat < -90:
            logging.debug('lat value out of range: %s' % row)
            self._increment_stat('bad latitude')
            return None
        lon = float(row['longitude'])
        if lon > 180 or lon < -180:
            logging.debug('lon value out of range: %s' % row)
            self._increment_stat('bad longitude')
            return None

        # skip rows with out of bounds score values
        score = float(row['score'])
        if score > MAX_SCORE or score < MIN_SCORE:
            logging.debug('score value out of range: %s' % row)
            self._increment_stat('bad score')
            return None

        # add a TileBounds gridcode
        row['gridcode'] = TileBounds.from_point(lon=lon, lat=lat, zoom_level=MAX_ZOOM).gridcode

        # Normalize score
        if score <= 0:
            row['score'] = 0
        elif 0 < score < 1:
            row['score'] = round(score * 0.6, 6)
        elif 1 <= score <= 5:
            row['score'] = round(((0.4 * (score - 1)) / 4) + 0.6, 6)

        row['longitude'] = round(lon, 6)
        row['latitude'] = round(lat, 6)
        row['timestamp'] = int(row['timestamp'])
        row['interval'] = 0
        row['type'] = TYPE_SEGMENT_START
        row['next_gridcode'] = None
        if self.prev_row:
            if self.prev_row['mmsi'] == row['mmsi']:
                self.prev_row['next_gridcode'] = row['gridcode']
                interval = row['timestamp'] - self.prev_row['timestamp']
                assert interval >= 0, 'input data must be sorted by mmsi, by timestamp'
                if interval <= MAX_INTERVAL:
                    row['type'] = TYPE_NORMAL
                    self.prev_row['interval'] += interval / 2
                    row['interval'] = interval / 2
                else:
                    self.prev_row['type'] = TYPE_SEGMENT_END
            else:
                self.prev_row['type'] = TYPE_SEGMENT_END

        result = self.prev_row
        self.prev_row = row
        return result

    def transform_file(self, infile, outfile):
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        fieldnames.extend(['gridcode', 'interval', 'type', 'next_gridcode'])
        writer = csv.DictWriter(outfile, fieldnames, lineterminator='\n')
        writer.writeheader()

        self.prev_row = None

        for row in reader:
            row_out = self.transform_row(row)
            if row_out:
                writer.writerow(row_out)
        if self.prev_row:
            self.prev_row['type'] = TYPE_SEGMENT_END
            writer.writerow(self.prev_row)


def main():
    arguments = docopt(__doc__, version='Pelagos AIS Transform 1.4')

    if arguments['--verbose']:
        log_level = logging.DEBUG
    elif arguments.get('--quiet'):
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    infile_name = arguments['INFILE']
    outfile_name = arguments['OUTFILE']

    #TODO: need error messaging for failures

    with sys.stdin if infile_name is None or '-' == infile_name else open(infile_name, 'rb') as csv_in:
        with sys.stdout if outfile_name is None or '-' == outfile_name else open(outfile_name, 'w') as csv_out:
            transform = Transform()
            transform.transform_file(csv_in, csv_out)
            logging.info(transform.stats)

    return 1


if __name__ == "__main__":
    sys.exit(main())
