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
#/*     Define TestGPBlacklistVessel() class
#/* ======================================================================= */#

class TestGPBlacklistVessel(unittest.TestCase):

    def test_get_scraper_options(self):
        self.assertIsInstance(scrape.gp_blacklist_vessel(None, get_scraper_options=True), dict)

    def test_get_output_fields(self):
        self.assertIsInstance(scrape.gp_blacklist_vessel(None, get_output_fields=True), list)

    def test_output(self):

        expected_output = {
            'http://blacklist.greenpeace.org/1/vessel/show/170-aladin': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: ICCAT Recommendation [03-04] relating to Mediterranean swordfish prohibits the use of driftnets for fisheries of large pelagics in the Mediterranean Sea. It is the responsibility of all ICCAT Contracting Parties to enforce this Recommendation and adopt a specific\r\nmanagement plan in order to protect the stock of swordfish in the Mediterranean Sea and sustain this fishery. This continued illegal activity should have come to an end when the European Union banned the use of driftnets for catching a wide range of pelagic fishes. EC Regulation EC/1239/98, that entered into force on January 2002.\nSource of IUU information: Vessel observed during Greenpeace Mediterranean Rainbow Warrior tour 2007',
                'callsign': 'Unknown',
                'class': 'Driftnetter',
                'controller_region': 'Tunisia',
                'date': '2007-06-20',
                'fishing_number': 'MO800',
                'flag': 'Tunisia',
                'imo': 'Unknown',
                'links': None,
                'mmsi': None,
                'name': 'Aladin',
                'notes': 'On the morning of 20 June 2007, a dozen vessels were spotted from the Rainbow Warrior, among them six Tunisian driftnet vessels which were identified as fishing on the high seas.',
                'owner_company': None,
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': None,
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/170-aladin',
                'vessel_length': None
            },
            'http://blacklist.greenpeace.org/1/vessel/show/161-biagio-anna': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: ICCAT Recommendation [03-04] relating to Mediterranean swordfish prohibits the use of driftnets for fisheries of large pelagics in the Mediterranean Sea. It is the responsibility of all ICCAT Contracting Parties to enforce this Recommendation and adopt a specific\r\nmanagement plan in order to protect the stock of swordfish in the Mediterranean Sea and sustain this fishery. This continued illegal activity should have come to an end when the European Union banned the use of driftnets for catching a wide range of pelagic fishes. EC Regulation EC/1239/98, that entered into force on January 2002.\nSource of IUU information: Vessel was observed by  Greenpeace Mediterranean Rainbow Warrior tour 2006',
                'callsign': 'Unknown',
                'class': 'Driftnetter',
                'controller_region': 'Italy',
                'date': '2009-04-26',
                'fishing_number': '03CS00822',
                'flag': 'Italy',
                'imo': 'Unknown',
                'links': None,
                'mmsi': None,
                'name': 'Biagio Anna',
                'notes': 'From 17 June to 15 July 2006, Greenpeace documented the activities of the Italian driftnet fleet targeting swordfish in the Thyrrenian and Ionian Seas. Five Italian vessels were found to be fishing for swordfish using driftnets. These data was presented to the 20th Regular Meeting of the ICCAT Commission in Antalya, November 2007. The information was not contested neither we know of any action taken against these vessels.',
                'owner_company': None,
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': None,
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/161-biagio-anna',
                'vessel_length': '12.2'
            },
            'http://blacklist.greenpeace.org/1/vessel/show/222-marcia-707': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: Illegal fishing inside Sierra Leone inshore zone\nSource of IUU information: http://www.lloydslistintelligence.com/llint/vessels/overview.htm?vesselId=123063&channel;=home\r\n\r\nhttp://ejfoundation.org/sites/default/files/public/Pirate%20Fishing%20Exposed.pdf\r\n\r\nhttps://webgate.ec.europa.eu/sanco/traces/output/KR/FFP_KR_fr.pdf',
                'callsign': '6MBA',
                'class': 'Trawler',
                'controller_region': 'Korea, Republic of',
                'date': '2011-01-18',
                'fishing_number': None,
                'flag': 'Korea, Republic of',
                'imo': '7205336',
                'links': None,
                'mmsi': None,
                'name': 'Marcia 707',
                'notes': 'Between January and March 2011, EJF documented four \rvessels fishing illegally in the inshore areas near Sherbro \rIsland in Sierra Leone: Medra, Marcia 707, 515 Amapola \rand Seta 70. All of the vessels are Korean-flagged and \raccredited to export their fish to the EU, though Medra \rhas also been listed as flagged to Honduras. The vessels \rwere responsible for causing extensive damage to local \rfishing equipment in the IEZ.',
                'owner_company': 'Bugang International Company Limited',
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': None,
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/222-marcia-707',
                'vessel_length': '57.7'
            },
            'http://blacklist.greenpeace.org/1/vessel/show/217-tawariq-1': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: Fishing without license against section 18',
                'callsign': 'A4DH8',
                'class': 'Longliner',
                'controller_region': 'Oman',
                'date': '2012-03-25',
                'fishing_number': None,
                'flag': 'Oman',
                'imo': "'8619376",
                'links': None,
                'mmsi': None,
                'name': 'Tawariq 1',
                'notes': '35 Crew members of FV TAWARIQ-1 and the Mombassa based ship agent of the fishing boat appeared before Dar-es-Salaam court of law on 2nd July, 2009  charged with fishing without a license contrary to section 18',
                'owner_company': 'Seas Tawariq Co LLC',
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': 'Odine Malagasy',
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/217-tawariq-1',
                'vessel_length': '43'
            }
        }

        for url, expected in expected_output.iteritems():
            actual = scrape.gp_blacklist_vessel(url)
            self.assertDictEqual(expected, actual)


#/* ======================================================================= */#
#/*     Define TestGPBlacklist() class
#/* ======================================================================= */#

class TestGPBlacklist(unittest.TestCase):

    def test_get_scraper_options(self):
        self.assertIsInstance(scrape.gp_blacklist(get_scraper_options=True), dict)

    def test_get_output_fields(self):
        self.assertIsInstance(scrape.gp_blacklist(get_output_fields=True), list)

    def test_return_urls(self):

        must_include = [
            'http://blacklist.greenpeace.org/1/vessel/show/33-feng-rong-shen',
            'http://blacklist.greenpeace.org/1/vessel/show/143-juanita-broken-up',
            'http://blacklist.greenpeace.org/1/vessel/show/168-ahmed-khalil',
            'http://blacklist.greenpeace.org/1/vessel/show/48-ying-jen-636',
            'http://blacklist.greenpeace.org/1/vessel/show/53-caribe'
        ]

        result = scrape.gp_blacklist(return_urls=True)
        for url in must_include:
            self.assertTrue(url in result)

    def test_return_results(self):

        expected = {
            'http://blacklist.greenpeace.org/1/vessel/show/170-aladin': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: ICCAT Recommendation [03-04] relating to Mediterranean swordfish prohibits the use of driftnets for fisheries of large pelagics in the Mediterranean Sea. It is the responsibility of all ICCAT Contracting Parties to enforce this Recommendation and adopt a specific\r\nmanagement plan in order to protect the stock of swordfish in the Mediterranean Sea and sustain this fishery. This continued illegal activity should have come to an end when the European Union banned the use of driftnets for catching a wide range of pelagic fishes. EC Regulation EC/1239/98, that entered into force on January 2002.\nSource of IUU information: Vessel observed during Greenpeace Mediterranean Rainbow Warrior tour 2007',
                'callsign': 'Unknown',
                'class': 'Driftnetter',
                'controller_region': 'Tunisia',
                'date': '2007-06-20',
                'fishing_number': 'MO800',
                'flag': 'Tunisia',
                'imo': 'Unknown',
                'links': None,
                'mmsi': None,
                'name': 'Aladin',
                'notes': 'On the morning of 20 June 2007, a dozen vessels were spotted from the Rainbow Warrior, among them six Tunisian driftnet vessels which were identified as fishing on the high seas.',
                'owner_company': None,
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': None,
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/170-aladin',
                'vessel_length': None
            },
            'http://blacklist.greenpeace.org/1/vessel/show/161-biagio-anna': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: ICCAT Recommendation [03-04] relating to Mediterranean swordfish prohibits the use of driftnets for fisheries of large pelagics in the Mediterranean Sea. It is the responsibility of all ICCAT Contracting Parties to enforce this Recommendation and adopt a specific\r\nmanagement plan in order to protect the stock of swordfish in the Mediterranean Sea and sustain this fishery. This continued illegal activity should have come to an end when the European Union banned the use of driftnets for catching a wide range of pelagic fishes. EC Regulation EC/1239/98, that entered into force on January 2002.\nSource of IUU information: Vessel was observed by  Greenpeace Mediterranean Rainbow Warrior tour 2006',
                'callsign': 'Unknown',
                'class': 'Driftnetter',
                'controller_region': 'Italy',
                'date': '2009-04-26',
                'fishing_number': '03CS00822',
                'flag': 'Italy',
                'imo': 'Unknown',
                'links': None,
                'mmsi': None,
                'name': 'Biagio Anna',
                'notes': 'From 17 June to 15 July 2006, Greenpeace documented the activities of the Italian driftnet fleet targeting swordfish in the Thyrrenian and Ionian Seas. Five Italian vessels were found to be fishing for swordfish using driftnets. These data was presented to the 20th Regular Meeting of the ICCAT Commission in Antalya, November 2007. The information was not contested neither we know of any action taken against these vessels.',
                'owner_company': None,
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': None,
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/161-biagio-anna',
                'vessel_length': '12.2'
            },
            'http://blacklist.greenpeace.org/1/vessel/show/222-marcia-707': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: Illegal fishing inside Sierra Leone inshore zone\nSource of IUU information: http://www.lloydslistintelligence.com/llint/vessels/overview.htm?vesselId=123063&channel;=home\r\n\r\nhttp://ejfoundation.org/sites/default/files/public/Pirate%20Fishing%20Exposed.pdf\r\n\r\nhttps://webgate.ec.europa.eu/sanco/traces/output/KR/FFP_KR_fr.pdf',
                'callsign': '6MBA',
                'class': 'Trawler',
                'controller_region': 'Korea, Republic of',
                'date': '2011-01-18',
                'fishing_number': None,
                'flag': 'Korea, Republic of',
                'imo': '7205336',
                'links': None,
                'mmsi': None,
                'name': 'Marcia 707',
                'notes': 'Between January and March 2011, EJF documented four \rvessels fishing illegally in the inshore areas near Sherbro \rIsland in Sierra Leone: Medra, Marcia 707, 515 Amapola \rand Seta 70. All of the vessels are Korean-flagged and \raccredited to export their fish to the EU, though Medra \rhas also been listed as flagged to Honduras. The vessels \rwere responsible for causing extensive damage to local \rfishing equipment in the IEZ.',
                'owner_company': 'Bugang International Company Limited',
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': None,
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/222-marcia-707',
                'vessel_length': '57.7'
            },
            'http://blacklist.greenpeace.org/1/vessel/show/217-tawariq-1': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: Fishing without license against section 18',
                'callsign': 'A4DH8',
                'class': 'Longliner',
                'controller_region': 'Oman',
                'date': '2012-03-25',
                'fishing_number': None,
                'flag': 'Oman',
                'imo': "'8619376",
                'links': None,
                'mmsi': None,
                'name': 'Tawariq 1',
                'notes': '35 Crew members of FV TAWARIQ-1 and the Mombassa based ship agent of the fishing boat appeared before Dar-es-Salaam court of law on 2nd July, 2009  charged with fishing without a license contrary to section 18',
                'owner_company': 'Seas Tawariq Co LLC',
                'previous_callsign': None,
                'previous_companies': None,
                'previous_flags': None,
                'previous_names': 'Odine Malagasy',
                'source': 'GreenpeaceBlacklist',
                'system': None,
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/217-tawariq-1',
                'vessel_length': '43'
            }
        }

        actual = scrape.gp_blacklist()
        for vessel in actual:
            if vessel['url'] in expected:
                self.assertDictEqual(expected[vessel['url']], vessel)


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main())
