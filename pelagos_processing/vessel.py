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
Vessel processing
"""


from __future__ import unicode_literals

import vectortile

from common import increment_stat
import settings


#/* ======================================================================= */#
#/*     Global variables
#/* ======================================================================= */#

TRANSFORM_RAW_ROW_STATS = {}


#/* ======================================================================= */#
#/*     Define normalize_score() function
#/* ======================================================================= */#

def normalize_score(score):

    """
    Normalize a vessel's likely-hood of fishing score to specific criteria


    Args:

        score (int): Vessel score


    Returns:

        Normalized vessel score
    """

    if score < 0:
        return 0
    else:
        return round(((score - settings.MIN_FISHING_SCORE) / (settings.MAX_FISHING_SCORE - settings.MIN_FISHING_SCORE)), 6)


#/* ======================================================================= */#
#/*     Define transform_raw_row() function
#/* ======================================================================= */#

def transform_raw_row(row, prev_row=None, zoom_level=15, type_segment_start=1, type_segment_end=2, max_interval=86400,
                      type_normal=0, log=settings.logging):
    
    """
    Transform a raw row of AIS data as delivered
    """

    global TRANSFORM_RAW_ROW_STATS

    # Latitude
    lat = float(row['latitude'])
    if -90 <= lat <= 90:
        row['latitude'] = round(lat, 6)
    else:
        log.debug('lat value out of range: %s' % row)
        increment_stat(TRANSFORM_RAW_ROW_STATS, 'bad_lat')
        return None

    # Longitude
    lng = float(row['longitude'])
    if -180 <= lng <= 180:
        row['longitude'] = round(lng, 6)
    else:
        log.debug('lon value out of range: %s' % row)
        increment_stat(TRANSFORM_RAW_ROW_STATS, 'bad_long')
        return None

    # Initial score
    score = float(row['score'])
    if settings.MIN_FISHING_SCORE <= score <= settings.MAX_FISHING_SCORE:
        row['score'] = normalize_score(score)
    else:
        log.debug('score value out of range: %s' % row)
        increment_stat(TRANSFORM_RAW_ROW_STATS, 'bad_score')
        return None
    
    # Add a TileBounds gridcode
    row['gridcode'] = str(vectortile.TileBounds.from_point(lon=lng, lat=lat, zoom_level=zoom_level))
    
    # Edit row
    row['timestamp'] = int(row['timestamp'])
    row['interval'] = 0
    row['type'] = type_segment_start
    row['next_gridcode'] = None
    
    if prev_row:
        if prev_row['mmsi'] == row['mmsi']:
            prev_row['next_gridcode'] = row['gridcode']
            interval = row['timestamp'] - prev_row['timestamp']
            assert interval >= 0, 'input data must be sorted by mmsi, by timestamp'
            if interval <= max_interval:
                row['type'] = type_normal
                prev_row['interval'] += interval / 2
                row['interval'] = interval / 2
            else:
                prev_row['type'] = type_segment_end
        else:
            prev_row['type'] = type_segment_start

    result = prev_row
    return result
