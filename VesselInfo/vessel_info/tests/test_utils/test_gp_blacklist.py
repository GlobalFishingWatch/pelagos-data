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
Unittests for vessel_info.utils.gp_blacklist
"""


from __future__ import unicode_literals

import csv
import os
from os.path import isfile
import sys
import unittest

from vessel_info import utils


#/* ======================================================================= */#
#/*     Define TestMain() function
#/* ======================================================================= */#

class TestMain(unittest.TestCase):

    def setUp(self):
        self.test_file = '.test_utils_TestMain_TestFile--_.csv.ext'
        if isfile(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if isfile(self.test_file):
            os.remove(self.test_file)

    def test_standard(self):

        sample_expected = {
            'http://blacklist.greenpeace.org/1/vessel/show/170-aladin': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: ICCAT Recommendation [03-04] relating to Mediterranean swordfish prohibits the use of driftnets for fisheries of large pelagics in the Mediterranean Sea. It is the responsibility of all ICCAT Contracting Parties to enforce this Recommendation and adopt a specific\r\nmanagement plan in order to protect the stock of swordfish in the Mediterranean Sea and sustain this fishery. This continued illegal activity should have come to an end when the European Union banned the use of driftnets for catching a wide range of pelagic fishes. EC Regulation EC/1239/98, that entered into force on January 2002.\nSource of IUU information: Vessel observed during Greenpeace Mediterranean Rainbow Warrior tour 2007',
                'callsign': 'Unknown',
                'class': 'Driftnetter',
                'controller_region': 'Tunisia',
                'date': '2007-06-20',
                'fishing_number': 'MO800',
                'flag': 'Tunisia',
                'imo': 'Unknown',
                'links': '',
                'mmsi': '',
                'name': 'Aladin',
                'notes': 'On the morning of 20 June 2007, a dozen vessels were spotted from the Rainbow Warrior, among them six Tunisian driftnet vessels which were identified as fishing on the high seas.',
                'owner_company': '',
                'previous_callsign': '',
                'previous_companies': '',
                'previous_flags': '',
                'previous_names': '',
                'source': 'GreenpeaceBlacklist',
                'system': '',
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/170-aladin',
                'vessel_length': ''
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
                'links': '',
                'mmsi': '',
                'name': 'Biagio Anna',
                'notes': 'From 17 June to 15 July 2006, Greenpeace documented the activities of the Italian driftnet fleet targeting swordfish in the Thyrrenian and Ionian Seas. Five Italian vessels were found to be fishing for swordfish using driftnets. These data was presented to the 20th Regular Meeting of the ICCAT Commission in Antalya, November 2007. The information was not contested neither we know of any action taken against these vessels.',
                'owner_company': '',
                'previous_callsign': '',
                'previous_companies': '',
                'previous_flags': '',
                'previous_names': '',
                'source': 'GreenpeaceBlacklist',
                'system': '',
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/161-biagio-anna',
                'vessel_length': '12.2'
            },
            'http://blacklist.greenpeace.org/1/vessel/show/222-marcia-707': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: Illegal fishing inside Sierra Leone inshore zone\nSource of IUU information: http://www.lloydslistintelligence.com/llint/vessels/overview.htm?vesselId=123063&channel;=home\r\n\r\nhttp://ejfoundation.org/sites/default/files/public/Pirate%20Fishing%20Exposed.pdf\r\n\r\nhttps://webgate.ec.europa.eu/sanco/traces/output/KR/FFP_KR_fr.pdf',
                'callsign': '6MBA',
                'class': 'Trawler',
                'controller_region': 'Korea, Republic of',
                'date': '2011-01-18',
                'fishing_number': '',
                'flag': 'Korea, Republic of',
                'imo': '7205336',
                'links': '',
                'mmsi': '',
                'name': 'Marcia 707',
                'notes': 'Between January and March 2011, EJF documented four \rvessels fishing illegally in the inshore areas near Sherbro \rIsland in Sierra Leone: Medra, Marcia 707, 515 Amapola \rand Seta 70. All of the vessels are Korean-flagged and \raccredited to export their fish to the EU, though Medra \rhas also been listed as flagged to Honduras. The vessels \rwere responsible for causing extensive damage to local \rfishing equipment in the IEZ.',
                'owner_company': 'Bugang International Company Limited',
                'previous_callsign': '',
                'previous_companies': '',
                'previous_flags': '',
                'previous_names': '',
                'source': 'GreenpeaceBlacklist',
                'system': '',
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/222-marcia-707',
                'vessel_length': '57.7'
            },
            'http://blacklist.greenpeace.org/1/vessel/show/217-tawariq-1': {
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: Fishing without license against section 18',
                'callsign': 'A4DH8',
                'class': 'Longliner',
                'controller_region': 'Oman',
                'date': '2012-03-25',
                'fishing_number': '',
                'flag': 'Oman',
                'imo': "'8619376",
                'links': '',
                'mmsi': '',
                'name': 'Tawariq 1',
                'notes': '35 Crew members of FV TAWARIQ-1 and the Mombassa based ship agent of the fishing boat appeared before Dar-es-Salaam court of law on 2nd July, 2009  charged with fishing without a license contrary to section 18',
                'owner_company': 'Seas Tawariq Co LLC',
                'previous_callsign': '',
                'previous_companies': '',
                'previous_flags': '',
                'previous_names': 'Odine Malagasy',
                'source': 'GreenpeaceBlacklist',
                'system': '',
                'url': 'http://blacklist.greenpeace.org/1/vessel/show/217-tawariq-1',
                'vessel_length': '43'
            }
        }

        # Make sure everything successfully ran
        args = ['-q', self.test_file]
        exit_code = utils.gp_blacklist.main(args)
        self.assertEqual(0, exit_code)
        self.assertTrue(isfile(self.test_file))

        # Re-running the same command should produce an error code of 1
        exit_code = utils.gp_blacklist.main(args)
        self.assertEqual(1, exit_code)
        self.assertTrue(isfile(self.test_file))

        # Re-running with overwrite should just re-run everything
        exit_code = utils.gp_blacklist.main(args + ['-overwrite'])
        self.assertEqual(0, exit_code)
        self.assertTrue(isfile(self.test_file))

        # Make sure output file is structured as expected
        with open(self.test_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['url'] in sample_expected:
                    self.assertDictEqual(sample_expected[row['url']], row)


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':
    sys.exit(unittest.main())
