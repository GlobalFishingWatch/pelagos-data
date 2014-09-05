#!/usr/bin/env python


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
Unittests for vessel_info.scrape
"""


from __future__ import unicode_literals

import requests.exceptions
import sys
import unittest

from vessel_info import scrape


#/* ======================================================================= */#
#/*     Define TestMMSI() class
#/* ======================================================================= */#

class TestMMSI(unittest.TestCase):
    
    #/* ----------------------------------------------------------------------- */#
    #/*     Define setUp() method
    #/* ----------------------------------------------------------------------- */#

    def setUp(self):
        self.mmsi = '266252000'
        self.expected_mt = {
            'name': 'NORDLINK',
            'class': 'Ro-ro/passenger ship',
            'callsign': 'SJPW',
            'imo': '9336256',
            'flag': 'Sweden',
            'system': 'AIS Marine Traffic',
            'mmsi': '266252000',
            'source': 'MarineTraffic'
        }
        self.expected_vf = {
            'callsign': 'SJPW',
            'class': 'Passenger/Ro-Ro Cargo Ship',
            'flag': 'Sweden',
            'imo': '9336256',
            'mmsi': '266252000',
            'name': 'NORDLINK',
            'source': 'VesselFinder',
            'system': None
        }
        self.expected_fm = {
            'callsign': None,
            'class': 'RoRo ship',
            'flag': 'SE|Sweden',
            'imo': 9336256,
            'mmsi': 266252000,
            'name': 'NORDLINK',
            'source': 'FleetMON',
            'system': None
        }

    #/* ----------------------------------------------------------------------- */#
    #/*     Define test_marine_traffic() method
    #/* ----------------------------------------------------------------------- */#

    def test_marine_traffic(self):

        # Standard use case
        scrape_mmsi = scrape.MMSI(self.expected_mt['mmsi'])
        actual = scrape_mmsi.marine_traffic()
        self.assertDictEqual(self.expected_mt, actual)

        # Check scraper options
        self.expected_mt['source'] = 'NEW_NAME'
        actual = scrape_mmsi.marine_traffic(name='NEW_NAME')
        self.assertDictEqual(self.expected_mt, actual)

        # Test with invalid MMSI
        scrape_mmsi = scrape.MMSI('INVALID----MMSI')
        self.assertRaises(requests.exceptions.HTTPError, scrape_mmsi.marine_traffic)

    #/* ----------------------------------------------------------------------- */#
    #/*     Define test_vessel_finder() method
    #/* ----------------------------------------------------------------------- */#

    def test_vessel_finder(self):

        # Standard use case
        scrape_mmsi = scrape.MMSI(self.expected_vf['mmsi'])
        actual = scrape_mmsi.vessel_finder()
        self.assertDictEqual(self.expected_vf, actual)

        # Check scraper options
        self.expected_vf['source'] = 'NEW_NAME'
        actual = scrape_mmsi.vessel_finder(name='NEW_NAME')
        self.assertDictEqual(self.expected_vf, actual)

        # Test with invalid MMSI
        scrape_mmsi = scrape.MMSI('INVALID----MMSI')
        self.assertRaises(requests.exceptions.HTTPError, scrape_mmsi.vessel_finder)

    #/* ----------------------------------------------------------------------- */#
    #/*     Define test_fleet_mon() method
    #/* ----------------------------------------------------------------------- */#

    def test_fleet_mon(self):

        # Standard use case
        scrape_mmsi = scrape.MMSI(self.expected_fm['mmsi'],
                                  fleetmon_api_user='skytruth_api',
                                  fleetmon_api_key='56703a82a81cf6ae67610c2e447259d75e023718')
        actual = scrape_mmsi.fleetmon()
        self.assertDictEqual(self.expected_fm, actual)

        # Check scraper options
        self.expected_fm['source'] = 'NEW_NAME'
        self.expected_fm['callsign'] = 'SJPW'
        actual = scrape_mmsi.fleetmon(callsign=True, name='NEW_NAME')
        self.assertDictEqual(self.expected_fm, actual)

        # Test with invalid MMSI
        scrape_mmsi = scrape.MMSI('INVALID----MMSI')
        self.assertRaises(requests.exceptions.HTTPError, scrape_mmsi.vessel_finder)


#/* ======================================================================= */#
#/*     Define TestAutoScrape() class
#/* ======================================================================= */#

class TestAutoScrape(unittest.TestCase):
    # TODO: Figure out how to test
    pass


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main(sys.argv))
