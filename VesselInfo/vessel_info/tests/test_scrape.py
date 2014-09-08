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
#/*     Define global variables
#/* ======================================================================= */#

FLEETMON_API_USER = 'skytruth_kevin'
FLEETMON_API_KEY = 'a0e7b74fc6bbd9c44c8359e20b01f903b3d6deaa'


#/* ======================================================================= */#
#/*     Define TestMMSI() class
#/* ======================================================================= */#

class TestMMSI(unittest.TestCase):
    
    #/* ----------------------------------------------------------------------- */#
    #/*     Define setUp() method
    #/* ----------------------------------------------------------------------- */#

    def setUp(self):

        # ** All string values are unicode **
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
            'imo': '9336256',
            'mmsi': '266252000',
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

        global FLEETMON_API_USER
        global FLEETMON_API_KEY

        # Standard use case
        scrape_mmsi = scrape.MMSI(self.expected_fm['mmsi'], fleetmon_api_user=FLEETMON_API_USER, fleetmon_api_key=FLEETMON_API_KEY)
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

    def test_fallback(self):

        global FLEETMON_API_KEY
        global FLEETMON_API_USER

        # Test an MMSI that failed for MarineTraffic but passed for VesselFinder
        scrape_mmsi = scrape.MMSI('207029000')
        actual = scrape.auto_scrape(scrape_mmsi, verbose=False, pause=1)
        expected = {
            'callsign': 'LZHL',
            'class': 'Bulk Carrier',
            'flag': 'Bulgaria',
            'imo': '8128145',
            'mmsi': '207029000',
            'name': 'SVILEN RUSSEV',
            'source': 'VesselFinder',
            'system': None
        }
        self.assertDictEqual(actual, expected)

        # Test an MMSI that failed for VesselFinder but passed for FleetMON
        scraper_options = {
            'fleetmon': {
                'api_user': FLEETMON_API_USER,
                'api_key': FLEETMON_API_KEY,
                'callsign': True
            }
        }
        scrape_mmsi = scrape.MMSI('570920')
        actual = scrape.auto_scrape(scrape_mmsi, verbose=False, pause=1, scraper_options=scraper_options)
        expected = {
            'callsign': 'WCB7066',
            'class': 'Tug',
            'flag': 'None|None',
            'imo': '8978693',
            'mmsi': '570920',
            'name': 'NRC SENTRY',
            'source': 'FleetMON',
            'system': None
        }
        self.assertDictEqual(expected, actual)

        # Make sure None is returned when a scraper fails
        # This MMSI is found by VesselFinder but not MarineTraffic so if MarineTraffic is the only enable scraper,
        # a value of None should be returned
        scrape_mmsi = scrape.MMSI('207029000')
        actual = scrape.auto_scrape(scrape_mmsi, verbose=False, pause=1, keep_scraper='marine_traffic')
        expected = None
        self.assertEqual(actual, expected)


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main())
