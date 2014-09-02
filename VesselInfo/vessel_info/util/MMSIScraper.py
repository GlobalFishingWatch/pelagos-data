#!/usr/bin/env python


# This document is part of the pelagos project
# https://github.com/skytruth/pelagos


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
Tools for scraping MMSI info
"""


from __future__ import print_function


__license__ = '''
The MIT License (MIT)

Copyright (c) 2014 SkyTruth

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


from bs4 import BeautifulSoup
import csv
import os
from os.path import *
import random
import requests
import sys
import time
import unittest


#/* ======================================================================= */#
#/*     Document level information and global variables
#/* ======================================================================= */#

__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_help_info', 'print_license', 'print_version',
           'ScrapeMMSI', 'main']

QUIET_MODE = False


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__version__ = '0.1-dev'
__release__ = '2014-07-03'
__author__ = 'Kevin Wurster'
__copyright__ = 'Copyright (c) 2014 SkyTruth'


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    vprint("""
{0} [--help-info] [--long-usage] [options]
{1} [-mfi mmsi_field] [-so option=val] [-p o_field_prefix]
{1} [--overwrite] [--subsample] input.csv output.csv
{1} input.csv output.csv
    """.format(__docname__, ' ' * len(__docname__)))


#/* ======================================================================= */#
#/*     Define print_long_usage() function
#/* ======================================================================= */#

def print_long_usage():

    """
    Print all commandline usage information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print_usage()
    vprint("""Options:
    -mfi --mmsi-field-name      Specify the field in the input csv that contains
                                the MMSI numbers.  Defaults to 'mmsi'.
    -p --prefix                 String prepended to all fields in the output
                                CSV - important to specify if the input CSV
                                contains fields that might be overwritten by
                                the scraper.  Defaults to 'v_'.
    -so --scraper-option        Specify options for the ScrapeMMSI() class.
                                More details can be found in the Scraper Options
                                section below
    -s --subsample              Only process part of the input file
    --overwrite                 Blindly overwrite the output file


Scraper Options: General
    agent=str                   Specify the user agent used in the
                                initial scraper request
    attempts=int                Max number of scrape attempts for each
                                site
    agent='random'|str          The user agent for the initial request
                                Specifying 'random' causes the scraper
                                to use a random user agent for each
                                request
    pause='random'|int          The amount of time to pause between each
                                scrape attempt.  Specifying 'random'
                                causes the scraper to pause for a
                                random amount of time between rp_min
                                and rp_max
    rp_min=int                  Minimum amount of time for pause='random'
                                Defaults to 0.
    rp_max=int                  Maximum amount of time for pause='random'
                                Defaults to 3.
    rp_precision=int            Precision used when rounding pause='random
                                Defaults to 1.

Scraper Options: MarineTraffic
    marinetraffic_base_url=str  Default base URL for MarineTraffic.com scrape
    """.format(__docname__, ' ' * len(__docname__)))  # ADD SCRAPER

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Print more detailed help information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print('''
Help: {0}" % __docname__)
------{1}
This utility takes an input CSV containing a field of MMSi numbers and attempts
to find various pieces of information about the vessel.  The input CSV can
contain any number of fields and the MMSI field can be explicitly defined with
the '-mfi' flag.  All input fields are preserved but they are re-ordered
alphabetically and all values are qualified in the output file.

In order to retrieve information, the utility takes an MMSI, pauses for a few
seconds to act more like a human, and scrapes a website until it gets information
or until it exhausts the allotted number of retries.  If the scrape retrieved
information from the very first website, it skips the rest adds the information
to the output CSV.  If all retries were exhausted for the first website, it
attempts to scrape the second, and so on.  The following websites are scraped
in this order:

  1. MarineTraffic.com

The pause between scrape attempts can be done in two ways.  By default the utility
waits somewhere between 0.1 and 3 seconds between scrape attempts but an explicit
pause value can be set with the '--pause' option.  This pause can also be completely
turned off with '--pause 0'.
    '''.format(__docname__, '-' * len(__docname__)))

    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print licensing information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print(__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    vprint("""
Help Flags:
    --help-info     This printout
    --help          More detailed description of this utility
    --usage         Arguments, parameters, etc.
    --long-usage    Usage plus brief description of all options
    --version       Version and ownership information
    --license       License information
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_version():

    """
    Print the module version information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    vprint("""
%s v%s - released %s

%s
    """ % (__docname__, __version__, __release__, __copyright__))

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_short_version():

    """
    Print the module version information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print(__version__)

    return 1


#/* ======================================================================= */#
#/*     Define ScrapeMMSI() class
#/* ======================================================================= */#

class ScrapeMMSI(object):

    output_fields = ['name', 'class', 'callsign', 'imo', 'flag', 'system', 'mmsi', 'source']
    user_agents = ['Mozilla/30.0']

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "ScrapeMMSI(%s, agent=%s, pause=%s)" % (self.mmsi, self.agent, str(self.pause))

    def __init__(self, mmsi, **kwargs):

        """
        Allow the user to scrape vessel information from specific sites

        :param mmsi: vessel's MMSI number
        :type mmsi: int|str
        :param agent: user agent for request
        :type: str

        :return: instance of ScrapeMMSI with a loaded MMSi
        :rtype: ScrapeMMSI()
        """

        # When adding or removing scrapers, search for the '# ADD SCRAPER' tag
        # to help find places where edits need to be made

        # MMSI
        self.mmsi = str(mmsi)

        # Parse other arguments
        self.agent = kwargs.get('agent', self.user_agents[0])
        self.attempts = kwargs.get('attempts', 3)
        self.pause = kwargs.get('pause', 'random')
        self.rp_min= kwargs.get('rp_min', 0.5)
        self.rp_max = kwargs.get('rp_max', 3)
        self.rp_precision = kwargs.get('precision', 1)
        self.null = kwargs.get('null', None)

        # Scraper specific information
        _scraper_order = kwargs.get('scraper_order', 'MarineTraffic').split(',')  # 'MarineTraffic, ADD SCRAPER'
        self.scraper_order = []
        for _scraper in _scraper_order:
            if _scraper.lower() == 'marinetraffic':
                self.scraper_order.append(self.scrape_marinetraffic)
            # ADD SCRAPER - append the method that does the scraping
        self.marinetraffic_base_url = kwargs.get('marinetraffic_base_url',
                                                 'http://www.marinetraffic.com/en/ais/details/ships')
        # ADD SCRAPER - Add a base URL

        # Validate
        if self.mmsi in (None, str(None)):
            raise ValueError("ERROR: Invalid MMSI: %s" % str(None))
        if isinstance(self.pause, str) and self.pause != 'random':
            raise ValueError("ERROR: Invalid pause option: %s" % self.pause)
        elif self.pause < 0:
            raise ValueError("ERROR: Invalid pause - must be > 0: %s" % str(self.pause))
        if self.rp_min > self.rp_max:
            raise ValueError("ERROR: Invalid rp_min/hp_max values: min=%s max=%s" % (str(self.rp_min), str(self.rp_max)))
        if self.rp_precision < 0:
            raise ValueError("ERROR: Invalid hp_precision value: %s" % str(self.rp_precision))
        if self.attempts < 1:
            raise ValueError("ERROR: Invalid number of attempts - must be >= 1: %s" % str(self.attempts))
        if not isinstance(self.marinetraffic_base_url, str):
            raise ValueError("ERROR: Invalid base URL for MarineTraffic: %s" % str(self.marinetraffic_base_url))

    #/* ----------------------------------------------------------------------- */#
    #/*     Define random_agent() method
    #/* ----------------------------------------------------------------------- */#

    def get_agent(self):

        """
        Get a random user agent for use in an HTTP request

        :return: a random user agent
        :rtype: str
        """
        if self.agent == 'random':
            return random.choice(self.user_agents)
        else:
            return self.agent

    #/* ----------------------------------------------------------------------- */#
    #/*     Define auto_scrape() method
    #/* ----------------------------------------------------------------------- */#

    def auto_scrape(self, site_scraper):

        """
        Keep trying to run a scraper until the max number of attempts are reached.
        Exceptions are silently caught and passed.

        Returns a populated dictionary on successful scrape and empty dictionary
        on failure.

        :param site_scraper: specific scraper method from THIS instance
        :type site_scraper: ScrapeMMSI.scrape_*

        :return: scraped vessel information
        :rtype: dict
        """

        scrape_result = {}

        attempt_counter = 0
        while attempt_counter < self.attempts:

            attempt_counter += 1

            # Pause
            time.sleep(self.get_pause())

            # Successful scrape
            try:
                scrape_result = site_scraper()
                break  # Got a successful scrape - no need to continue trying

            # Some failure
            except Exception:
                pass

        return scrape_result.copy()

    #/* ----------------------------------------------------------------------- */#
    #/*     Define full_scrape() method
    #/* ----------------------------------------------------------------------- */#

    def full_scrape(self):

        """
        Run all scrapers through auto_scrape() method

        :return: vessel info or empty dict
        :rtype: dict
        """

        for scraper in self.scraper_order:

            result = self.auto_scrape(scraper)

            if result:
                return result


    #/* ----------------------------------------------------------------------- */#
    #/*     Define get_pause() method
    #/* ----------------------------------------------------------------------- */#

    def get_pause(self):

        """
        Figure out how long to pause between scrape attempts

        :return:
        :rtype:
        """

        if self.pause == 'random':
            return round(random.uniform(self.rp_min, self.rp_max), self.rp_precision)
        else:
            return self.pause

    #/* ----------------------------------------------------------------------- */#
    #/*     Define scrape_marinetraffic() method
    #/* ----------------------------------------------------------------------- */#

    def scrape_marinetraffic(self, scraper_name='MarineTraffic'):

        """
        Scrape MarineTraffic.com for vessel information

        A dictionary is returned containing all fields stored as strings:

        {'name': 'NORDLINK',
         'class': 'Ro-ro/passenger ship',
         'callsign': 'SJPW',
         'imo': '9336256',
         'flag': 'Sweden',
         'system': 'AIS Marine Traffic',
         'mmsi': '266252000'}

        :return: vessel information as outlined above
        :rtype: dict
        """

        # Make request
        response = requests.get(self.marinetraffic_base_url + '/' + self.mmsi, headers={'User-agent': self.get_agent()})
        try:
            response.raise_for_status()
        except Exception, e:
            vprint(e)
            vprint("MMSI: %s" % str(self.mmsi))

        # Load HTML into beautiful soup and then parse all meta tags trying to find:
        # <meta property='og:title' content='NORDLINK - Ro-ro/passenger ship: current position and details | IMO 9336256, MMSI 266252000, Callsign SJPW | Registered in Sweden - AIS Marine Traffic'/>
        soup = BeautifulSoup(response.text)
        response.close()
        content = None
        for item in soup.find_all('meta'):
            if item.get('property') == 'og:title':
                content = item.get('content')
                break

        # If content was found extract information
        if content is None:
            output = None

        else:

            # The comment preceding each extraction explains what it is doing and how it relates to the
            # following example line:
            # 'NORDLINK - Ro-ro/passenger ship: current position and details | IMO 9336256, MMSI 266252000, Callsign SJPW | Registered in Sweden - AIS Marine Traffic'
            output = {}

            # Give the user a way to figure out where this information actually came from
            if 'source' in self.output_fields:
                output['source'] = scraper_name

            # Vessel name: NORDLINK
            if 'name' in self.output_fields:
                try:
                    output['name'] = str(content.split(' - ')[0].strip())
                except IndexError:
                    output['name'] = self.null

            # Vessel class: Ro-ro/passenger ship
            if 'class' in self.output_fields:
                try:
                    output['class'] = str(content.split(' - ')[1].split(':')[0].strip())
                except IndexError:
                    output['class'] = self.null

            # Vessel Callsign: SJPW
            if 'callsign' in self.output_fields:
                try:
                    output['callsign'] = str(content.split('Callsign ')[1].split(' |')[0].strip())
                except IndexError:
                    output['callsign'] = self.null

            # Vessel IMO number: 9336256
            if 'imo' in self.output_fields:
                try:
                    output['imo'] = str(content.split('IMO ')[1].split(',')[0].strip())
                except IndexError:
                    output['imo'] = self.null

            # Vessel flag: Sweden
            if 'flag' in self.output_fields:
                try:
                    output['flag'] = str(content.split('Registered in ')[1].split(' -')[0].strip())
                except IndexError:
                    output['flag'] = self.null

            # Vessel tracking system: AIS Marine Traffic
            if 'system' in self.output_fields:
                try:
                    output['system'] = str(content.split(' - ')[-1].strip())
                except IndexError:
                    output['system'] = self.null

            # Vessel MMSI number from content: 266252000
            if 'mmsi' in self.output_fields:
                try:
                    output['mmsi'] = str(content.split('MMSI')[1].split(',')[0].strip())
                except IndexError:
                    output['mmsi'] = self.null

            # Make sure a reference isn't returned
            output = output.copy()

        # Return output
        return output

    #/* ----------------------------------------------------------------------- */#
    #/*     # ADD SCRAPER - new method for specific site
    #/* ----------------------------------------------------------------------- */#

    # ADD SCRAPER - def scrape_new_site()


#/* ======================================================================= */#
#/*     Define TestScrapeMMSI() class
#/* ======================================================================= */#


class TestScrapeMMSI(unittest.TestCase):

    def setUp(self):
        self.valid_mmsi = 9008639
        self.invalid_mmsi = -0
        self.incomplete_mmsi = 224156290
        pass

    def test_validate_arguments(self):

        # Test argument validations
        self.assertRaises(ValueError, ScrapeMMSI, None)
        self.assertRaises(ValueError, ScrapeMMSI, 'None')
        self.assertRaises(ValueError, ScrapeMMSI, '', pause='invalid_string_option')
        self.assertRaises(ValueError, ScrapeMMSI, '', pause=-1)
        self.assertRaises(ValueError, ScrapeMMSI, '', rp_min=1, rp_max=0)
        self.assertRaises(ValueError, ScrapeMMSI, '', attempts=0)
        self.assertRaises(ValueError, ScrapeMMSI, '', marinetraffic_base_url=None)

        # Test with valid arguments
        self.assertIsInstance(ScrapeMMSI(self.valid_mmsi, pause=1, rp_min=0, rp_max=1, attempts=1,
                                         marinetraffic_base_url='empty_string'), ScrapeMMSI)

    def test_get_agent(self):

        # Test with a specific user agent
        ua = 'Mozilla/30.0'
        for i in range(10):
            scraper = ScrapeMMSI('', agent=ua)
            self.assertEqual(scraper.get_agent(), scraper.agent)
            self.assertEqual(scraper.agent, ua)
            self.assertEqual(scraper.get_agent(), ua)

        # Test with a random agent
        ua = 'random'
        for i in range(10):
            scraper = ScrapeMMSI('', agent=ua)
            self.assertTrue(scraper.get_agent() in ScrapeMMSI.user_agents)

        # Test the default agent
        for i in range(10):
            scraper = ScrapeMMSI('')
            self.assertEqual(scraper.get_agent(), ScrapeMMSI.user_agents[0])

    def test_get_pause(self):

        # Test with an explicit pause
        p = 10
        for i in range(10):
            scraper = ScrapeMMSI('', pause=10)
            self.assertEqual(scraper.get_pause(), scraper.pause)
            self.assertEqual(scraper.get_pause(), p)
            self.assertEqual(scraper.pause, p)

        # Test with a human pause options
        for i in range(10):
            scraper = ScrapeMMSI('', pause='random')
            self.assertTrue(scraper.rp_min <= scraper.get_pause() <= scraper.rp_max)

        # Test the default pause
        for i in range(10):
            scraper = ScrapeMMSI('')
            self.assertTrue(scraper.rp_min <= scraper.get_pause() <= scraper.rp_max)

    def test_scrape_marinetraffic(self):

        # Default behavior
        scraper = ScrapeMMSI(266252000)
        expected = {'name': 'NORDLINK',
                    'class': 'Ro-ro/passenger ship',
                    'callsign': 'SJPW',
                    'imo': '9336256',
                    'flag': 'Sweden',
                    'system': 'AIS Marine Traffic',
                    'mmsi': '266252000',
                    'source': 'MarineTraffic'}
        actual = scraper.scrape_marinetraffic()
        self.assertDictEqual(expected, actual)

        # Change default scraper name
        scraper = ScrapeMMSI(266252000)
        expected = {'name': 'NORDLINK',
                    'class': 'Ro-ro/passenger ship',
                    'callsign': 'SJPW',
                    'imo': '9336256',
                    'flag': 'Sweden',
                    'system': 'AIS Marine Traffic',
                    'mmsi': '266252000',
                    'source': 'NEW_MarineTraffic'}
        actual = scraper.scrape_marinetraffic(scraper_name='NEW_MarineTraffic')
        self.assertDictEqual(expected, actual)

    def test_auto_scrape(self):

        expected = {'name': 'NORDLINK',
                    'class': 'Ro-ro/passenger ship',
                    'callsign': 'SJPW',
                    'imo': '9336256',
                    'flag': 'Sweden',
                    'system': 'AIS Marine Traffic',
                    'mmsi': '266252000',
                    'source': 'MarineTraffic'}

        scraper = ScrapeMMSI(266252000)
        actual = scraper.auto_scrape(scraper.scrape_marinetraffic)
        self.assertDictEqual(expected, actual)

    def test_full_scrape(self):

        expected = {'name': 'NORDLINK',
                    'class': 'Ro-ro/passenger ship',
                    'callsign': 'SJPW',
                    'imo': '9336256',
                    'flag': 'Sweden',
                    'system': 'AIS Marine Traffic',
                    'mmsi': '266252000',
                    'source': 'MarineTraffic'}

        scraper = ScrapeMMSI(266252000)
        actual = scraper.full_scrape()
        self.assertDictEqual(expected, actual)



#/* ======================================================================= */#
#/*     Define TestMain() class
#/* ======================================================================= */#

class TestMain(unittest.TestCase):

    #/* ----------------------------------------------------------------------- */#
    #/*     Define setUp() method
    #/* ----------------------------------------------------------------------- */#

    def setUp(self):

        """
        Define test content and write test input file
        """

        self.i_test_file = 'I_TEST_FILE_ScrapeMMSI.csv'
        self.o_test_file = 'O_TEST_FILE_ScrapeMMSI.csv'
        self.test_content = [{'STATIC': 'STATIC', 'name': 'NORDLINK', 'class': 'Ro-ro/passenger ship',
                              'callsign': 'SJPW', 'imo': '9336256', 'flag': 'Sweden', 'system': 'AIS Marine Traffic',
                              'mmsi': '266252000', 'source': 'MarineTraffic'}]

        # Write test input file
        with open(self.i_test_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['mmsi', 'STATIC'])
            writer.writeheader()
            for row in self.test_content:
                content = {'STATIC': row['STATIC'],
                           'mmsi': row['mmsi']}
                writer.writerow(content.copy())

    #/* ----------------------------------------------------------------------- */#
    #/*     Define tearDown() method
    #/* ----------------------------------------------------------------------- */#

    def tearDown(self):

        """
        Delete test files
        """

        # Delete test files
        for item in (self.i_test_file, self.o_test_file):
            if isfile(item):
                os.remove(item)

    #/* ----------------------------------------------------------------------- */#
    #/*     Define test_main_default() method
    #/* ----------------------------------------------------------------------- */#

    def test_main_default(self):

        """
        Test default behavior - take a CSV, read the MMSI field, run all scrapers,
        write and write an output file containing all input fields plus the new
        vessel info fields.
        """

        result = main(['--quiet', '--prefix', '', '-so', 'pause=0', self.i_test_file, self.o_test_file])
        self.assertEqual(result, 0)

        with open(self.o_test_file, 'r') as o_f:

            reader = csv.DictReader(o_f)
            o_lines = [i for i in reader]

            # Compare input lines to output lines
            self.assertListEqual(o_lines, self.test_content)


#/* ======================================================================= */#
#/*     Define vprint() function
#/* ======================================================================= */#

def vprint(message):

    """
    Easily handle switching verbosity on and off for PRINT statements

    :param message: message to be printed

    :return: None
    :rtype: None
    """

    global QUIET_MODE

    if not QUIET_MODE:
        print(message)


#/* ======================================================================= */#
#/*     Define vwrite() function
#/* ======================================================================= */#

def vwrite(message, stream=sys.stdout):

    """
    Easily handle switching verbosity on and off for stream.write() statements

    :param message: message to be written to stream

    :return: None
    :rtype: None
    """

    global QUIET_MODE

    if not QUIET_MODE:
        stream.write(message)
        stream.flush()


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
    Commandline logic

    :param args: arguments gathered from the commandline
    :type args: list

    :return: returns 0 on success and 1 on error
    :rtype: int
    """

    global QUIET_MODE

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    # Processing options
    overwrite_mode = False
    subsample = None
    i_csv_mmsi_field = 'mmsi'
    o_field_prefix = 'v_'

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    input_csv_file = None
    output_csv_file = None

    scraper_options = {}

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse Arguments
    #/* ----------------------------------------------------------------------- */#

    i = 0
    arg_error = False
    while i < len(args):

        try:
            arg = args[i]

            # Help arguments
            if arg in ('--help', '-help'):
                return print_help()
            elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo', '-h'):
                return print_help_info()
            elif arg in ('--license', '-license'):
                return print_license()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--long-usage', '-long-usage', '-lu'):
                return print_long_usage()
            
            # Input CSV options
            elif arg in ('-mfi', '--mmsi-field-name'):
                i += 2
                i_csv_mmsi_field = args[i - 1]

            # Configure the scraper
            elif arg in ('--scraper-option', '-so'):
                i += 2
                key, val = args[i - 1].split('=')
                scraper_options[key] = val

            # Output file options
            elif arg in ('-p', '--prefix'):
                i += 2
                o_field_prefix = args[i - 1]

            # Additional options
            elif arg in ('-overwrite', '--overwrite'):
                i += 1
                overwrite_mode = True
            elif arg in ('-s', '--subsample'):
                i += 2
                subsample = args[i - 1]
            elif arg in ('-q', '--quiet'):
                i += 1
                QUIET_MODE = True

            # Positional arguments and errors
            else:

                i += 1

                # Catch input CSV
                if input_csv_file is None:
                    input_csv_file = abspath(arg)

                # Catch output CSV
                elif output_csv_file is None:
                    output_csv_file = abspath(arg)

                # Catch unrecognized arguments
                else:
                    arg_error = True
                    vprint("ERROR: Unrecognized argument: %s" % arg)

        # An argument with parameters likely didn't iterate 'i' properly
        except IndexError:
            i += 1
            arg_error = True
            vprint("ERROR: An argument has invalid parameters")

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate Configuration
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        vprint("ERROR: Did not successfully parse arguments")

    # Check input CSV
    if not os.access(input_csv_file, os.R_OK):
        bail = True
        vprint("ERROR: Input CSV doesn't exist or needs read permission: %s" % input_csv_file)
    else:
        with open(input_csv_file, 'r') as f:
            reader = csv.DictReader(f)
            if i_csv_mmsi_field not in reader.fieldnames:
                vprint("ERROR: MMSI field '%s' not in: %s" % (i_csv_mmsi_field, input_csv_file))
                return 1

    # Check output csv
    if isfile(output_csv_file) and not overwrite_mode:
        bail = True
        vprint("ERROR: Overwrite=%s and output CSV exists: %s" % (str(overwrite_mode), output_csv_file))
    elif isfile(output_csv_file) and overwrite_mode and not os.access(output_csv_file, os.W_OK):
        bail = True
        vprint("ERROR: Need write permission on output CSV: %s" % output_csv_file)
    elif not os.access(dirname(output_csv_file), os.W_OK):
        bail = True
        vprint("ERROR: Need write permission for output directory: %s" % dirname(output_csv_file))

    # Check subsample
    if subsample is not None:
        try:
            subsample = int(subsample)
            if not subsample > 0:
                bail = True
                vprint("ERROR: Subsample must be > 0: %s" % str(subsample))
        except ValueError:
            bail = True
            vprint("ERROR: Subsample must be an int: %s" % str(subsample))

    # Check scraper options
    # Transform scraper options to python types
    for key, val in scraper_options.copy().iteritems():
        if val.isdigit():
            scraper_options[key] = int(val)
        elif val == 'None':
            scraper_options[key] = None
        else:
            try:
                scraper_options[key] = float(val)
            except ValueError:
                pass

    # Check to see if all of the scraper options will pass the argument validation
    try:
        ScrapeMMSI('', **scraper_options)
    except ValueError, e:
        print(e)
        return 1

    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Prep datasources
    #/* ----------------------------------------------------------------------- */#

    # Create a field map connecting scraper output fields to desired output field names
    o_field_map = {field: o_field_prefix + field for field in ScrapeMMSI.output_fields}

    # Figure out how many data rows are in the input CSV
    num_rows = None
    with open(input_csv_file, 'r') as f:
        num_rows = len([i for i in csv.DictReader(f)])

    # Adjust subsample if necessary
    if subsample is not None and subsample > num_rows:
        print_function("Subsample is greater than number of input rows - processing all")
        subsample = None

    # Set up input file
    row_counter = 0
    with open(input_csv_file, 'r') as i_csv_f:
        reader = csv.DictReader(i_csv_f)

        # Set up output file
        with open(output_csv_file, 'w') as o_csv_f:

            # Create output CSV writer and immediately write header
            writer = csv.DictWriter(o_csv_f, reader.fieldnames + o_field_map.values())
            writer.writeheader()

            #/* ----------------------------------------------------------------------- */#
            #/*     Process input CSV
            #/* ----------------------------------------------------------------------- */#

            # Process all input CSV rows
            for row in reader:

                # Update user
                row_counter += 1
                vwrite("\r\x1b[K" + "    %s/%s" % (str(row_counter), str(num_rows)))

                # Cache information
                mmsi = row[i_csv_mmsi_field]

                # Load the MMSI into the scraper class
                scraper = ScrapeMMSI(mmsi, **scraper_options)

                #/* ----------------------------------------------------------------------- */#
                #/*     Attempt scrapes
                #/* ----------------------------------------------------------------------- */#

                scrape_result = None

                # Process all scrapers in order until one produces a valid result
                for site_scraper in scraper.scraper_order:

                    # Only execute the next scraper if the previous failed
                    if scrape_result is None:

                        # Scraper's yield errors, a dict, or False - keep printing the errors
                        # until a dict or False is found
                        attempt_counter = 0
                        while attempt_counter < scraper.attempts:

                            attempt_counter += 1

                            # Pause
                            time.sleep(scraper.get_pause())

                            # Successful scrape
                            try:
                                scrape_result = site_scraper()
                                break  # Got a successful scrape - no need to continue trying

                            # Got an error - print it out
                            except Exception, e:
                                vprint("\r\x1b[K" + "    %s/%s - MMSI:%s attempt %s - %s" %
                                      (str(row_counter), str(num_rows), str(mmsi), str(attempt_counter), e))

                        # Did not have a successful scrape
                        if scrape_result is None:
                            vprint("\r\x1b[K" + "    %s/%s - MMSI:%s attempt %s - %s" %
                                  (str(row_counter), str(num_rows), str(mmsi), str(attempt_counter), 'FAILED'))

                #/* ----------------------------------------------------------------------- */#
                #/*     Write results
                #/* ----------------------------------------------------------------------- */#

                # Didn't get a successful scrape - populate null values
                if scrape_result is None:
                    scrape_result = {field: scraper.null for field in ScrapeMMSI.output_fields}

                # Transform fields into output fields based on the field map
                scrape_result = {o_field_map[key]: val for key, val in scrape_result.copy().iteritems()}

                # Write the output row
                writer.writerow(dict(row.items() + scrape_result.items()))

                #/* ----------------------------------------------------------------------- */#
                #/*     Subsample check
                #/* ----------------------------------------------------------------------- */#

                # Check to see if the subsample has been fulfilled
                if subsample is not None and row_counter > subsample:
                    vprint(" - Completed subsample")
                    break

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup
    #/* ----------------------------------------------------------------------- */#

    # Success
    vprint(" - Done")  # Required formatting due to sys.stdout.flush()
    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Run unittests
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':
        del sys.argv[1]
        sys.exit(unittest.main())

    # Remove script name and give the rest to main
    elif len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))

    # Didn't get enough arguments - print usage
    else:
        sys.exit(print_usage())
