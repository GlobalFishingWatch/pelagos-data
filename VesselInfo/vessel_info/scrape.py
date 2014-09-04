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
Utilities required for collecting vessel information from a variety of websites
"""


from __future__ import unicode_literals

import json
import random
import requests
import sys
import time

from bs4 import BeautifulSoup


#/* ======================================================================= */#
#/*     Define global variables
#/* ======================================================================= */#

DEFAULT_RETRY = 3
DEFAULT_PAUSE = 1
DEFAULT_PAUSE_MIN = 0
DEFAULT_PAUSE_MAX = 3
DEFAULT_TIMEOUT = 30
USER_AGENTS = ['Mozilla/30.0']


#/* ======================================================================= */#
#/*     Define ScrapeMMSI() class
#/* ======================================================================= */#

class MMSI(object):

    """
    Load an MMSI and scrape vessel info from various sources
    """

    # Used to build documentation and to check validity of scraper options
    scraper_options = {
        'marine_traffic': {
            'name': "(str): Scraper identifier - placed in output 'source' field",
            'base_url': "(str): Root URL to which parameters are appended",
            'headers': "(dict): Header parameter for each scrape request",
            'timeout': "(int): Number of seconds to wait until a scrape request is considered a failure"
        },
        'vessel_finder': {
            'name': "(str): Scraper identifier - placed in output 'source' field",
            'base_url': "(str): Root URL to which parameters are appended",
            'headers': "(dict): Header parameter for each scrape request",
            'timeout': "(int): Number of seconds to wait until a scrape request is considered a failure"
        },
        'fleetmon': {
            'name': "(str): Scraper identifier - placed in output 'source' field",
            'base_url': "(str): Root URL to which parameters are appended",
            'headers': "(dict): Header parameter for each scrape request",
            'api_key': "(str): FleetMON API key matching api_user",
            'api_user': "(str): FleetMON username matching api_key",
            'callsign': "(bool): Set to 'True' to enable callsign scraping",
            'timeout': "(int): Number of seconds to wait until a scrape request is considered a failure"
        }
    }

    # Used in batch mode to determine which order the scrapers should be called
    scraper_order = ['marine_traffic', 'vessel_finder', 'fleetmon']

    # Referenced by batch processing algorithms to prep output CSV for additional fields
    ofields = ['name', 'class', 'callsign', 'imo', 'flag', 'system', 'mmsi', 'source']

    #/* ----------------------------------------------------------------------- */#
    #/*     Define __repr__() method
    #/* ----------------------------------------------------------------------- */#

    def __repr__(self):
        return "%s(%s, user_agent=%s, null=%s, timeout=%s)" \
               % (self.__class__.__name__, self.mmsi, self.user_agent, self.null, self.timeout)

    #/* ----------------------------------------------------------------------- */#
    #/*     Define __str__() method
    #/* ----------------------------------------------------------------------- */#

    def __str__(self):
        return self.__repr__()

    #/* ----------------------------------------------------------------------- */#
    #/*     Define __init__() method
    #/* ----------------------------------------------------------------------- */#

    def __init__(self, mmsi, user_agent=None, null=None, timeout=DEFAULT_TIMEOUT):

        """Collect vessel information by scraping specific websites

        Args:
            mmsi (str|int):

        Kwargs:
            user_agent (str): Used in the request header to specify which browser
                is supposedly making the request.  By default a random user agent
                is selected but the user may override with this arg
            null: By default information about a vessel that cannot be found
                will be set to None in the dict each scraper returns but the
                user may override with this arg
        """

        global USER_AGENTS

        self.mmsi = mmsi
        self.null = null
        self.timeout = timeout
        if user_agent is None or user_agent.lower() == 'random':
            self.user_agent = random.choice(USER_AGENTS)
        else:
            self.user_agent = user_agent

        # Output template for scrapers to dump info into
        self.output_template = {
            'name': self.null,
            'class': self.null,
            'callsign': self.null,
            'imo': self.null,
            'flag': self.null,
            'system': self.null,
            'mmsi': self.null,
            'source': self.null
        }

    #/* ----------------------------------------------------------------------- */#
    #/*     Define marine_traffic() method
    #/* ----------------------------------------------------------------------- */#

    def marine_traffic(self, **kwargs):

        """
        Scrape MarineTraffic.com/<MMSI> for vessel information


        Kwargs:

            name (str): Included in output in 'source' key

            base_url (str): URL + mmsi = HTML containing vessel information

            headers (dict): Request header - defaults to {'User-agent': self.user_agent}


        Returns:

            Failure: None

            Success: A dictionary containing the following vessel information:

                {
                    'name': 'NORDLINK',
                    'class': 'Ro-ro/passenger ship',
                    'callsign': 'SJPW',
                    'imo': '9336256',
                    'flag': 'Sweden',
                    'system': 'AIS Marine Traffic',
                    'mmsi': '266252000',
                    'source': 'MarineTraffic'
                }

            Fields that cannot be collected are set to the user specified null value
            which defaults to None


        Raises:

            requests.exceptions.*: Exceptions can be raised by the initial request
                but none are suppressed
        """

        name = kwargs.get('name', 'MarineTraffic')
        base_url = kwargs.get('base_url', 'http://www.marinetraffic.com/en/ais/details/ships/')
        headers = kwargs.get('headers', {'User-agent': self.user_agent})
        timeout = kwargs.get('timeout', self.timeout)

        if base_url[-1] != '/':
            base_url += '/'

        # Make request and check for errors
        response = requests.get(base_url + self.mmsi, timeout=timeout, headers=headers)
        response.raise_for_status()

        # Load HTML into beautiful soup and then parse all meta tags trying to find:
        # <meta property='og:title' content='NORDLINK - Ro-ro/passenger ship: current position and details | IMO 9336256, MMSI 266252000, Callsign SJPW | Registered in Sweden - AIS Marine Traffic'/>
        soup = BeautifulSoup(response.text)
        response.close()

        content = None
        for item in soup.find_all('meta'):
            if item.get('property') == 'og:title':
                content = item.get('content')
                break

        # No content - return None
        if content is None:
            output = None

        # Found content - extract
        else:

            output = self.output_template.copy()
            output['source'] = name

            # The comment preceding each extraction explains what it is doing and how it relates to the
            # following example line:
            # 'NORDLINK - Ro-ro/passenger ship: current position and details | IMO 9336256, MMSI 266252000, Callsign SJPW | Registered in Sweden - AIS Marine Traffic'

            # Vessel name: NORDLINK
            try:
                output['name'] = content.split(' - ')[0].strip()
            except IndexError:
                output['name'] = self.null

            # Vessel class: Ro-ro/passenger ship
            try:
                output['class'] = content.split(' - ')[1].split(':')[0].strip()
            except IndexError:
                output['class'] = self.null

            # Vessel Callsign: SJPW
            try:
                output['callsign'] = content.split('Callsign ')[1].split(' |')[0].strip()
            except IndexError:
                output['callsign'] = self.null

            # Vessel IMO number: 9336256
            try:
                output['imo'] = content.split('IMO ')[1].split(',')[0].strip()
            except IndexError:
                output['imo'] = self.null

            # Vessel flag: Sweden
            try:
                output['flag'] = content.split('Registered in ')[1].split(' -')[0].strip()
            except IndexError:
                output['flag'] = self.null

            # Vessel tracking system: AIS Marine Traffic
            try:
                output['system'] = content.split(' - ')[-1].strip()
            except IndexError:
                output['system'] = self.null

            # Vessel MMSI number from content: 266252000
            try:
                output['mmsi'] = content.split('MMSI')[1].split(',')[0].strip()
            except IndexError:
                output['mmsi'] = self.null

            output = output.copy()

        soup = None
        return output

    #/* ----------------------------------------------------------------------- */#
    #/*     Define vessel_finder() method
    #/* ----------------------------------------------------------------------- */#

    def vessel_finder(self, **kwargs):

        """
        Scrape VesselFinder.com/vessels/0-IMO-0-MMSI-<MMSI> for vessel information


        Kwargs:

            name (str): Included in output in 'source' key

            base_url (str): URL + mmsi = HTML containing vessel information

            headers (dict): Request header - defaults to {'User-agent': self.user_agent}


        Returns:

            Failure: None

            Success: A dictionary containing the following vessel information:

                {
                    'name': 'NORDLINK',
                    'class': 'Passenger/Ro-Ro Cargo Ship',
                    'callsign': 'SJPW',
                    'imo': '9336256',
                    'flag': 'Sweden',
                    'system': None,
                    'mmsi': '266252000',
                    'source': 'VesselFinder
                }

            Fields that cannot be collected are set to the user specified null value
            which defaults to None.

            NOTE: The 'system' field cannot be collected


        Raises:

            requests.exceptions.*: Exceptions can be raised by the initial request
                but none are suppressed

            ValueError: If a BeautifulSoup parse returns unexpected results
        """

        name = kwargs.get('name', 'VesselFinder')
        base_url = kwargs.get('base_url', 'http://www.vesselfinder.com/vessels/')
        headers = kwargs.get('headers', {'User-agent': self.user_agent})
        timeout = kwargs.get('timeout', self.timeout)

        if base_url[-1] != '/':
            base_url += '/'

        # Make request and check for errors
        request_url = base_url + '0-IMO-0-MMSI-%s' % self.mmsi
        response = requests.get(request_url, timeout=timeout, headers=headers)
        response.raise_for_status()

        # Load HTML into beautiful soup and then parse all meta tags trying to find:
        # <meta property='og:title' content='NORDLINK - Ro-ro/passenger ship: current position and details | IMO 9336256, MMSI 266252000, Callsign SJPW | Registered in Sweden - AIS Marine Traffic'/>
        soup = BeautifulSoup(response.text)
        response.close()

        # Get the lines containing
        details = soup.find_all('div', {'class': 'ship-details-section'})
        if not details:
            info_lines = None
        elif len(details) is not 1:
            # TODO: Investigate this condition - during testing all MMSI's only had a single element in details
            raise ValueError("Unexpected BeautifulSoup result")
        else:
            info_lines = details[0].find_all('span', {'class': 'value'})

        # No content - return None
        if info_lines in (None, []):
            output = None

        # Found content - extract
        else:

            # System denotes which tracking system (AIS, VMS, etc.) the vessel's info was extracted from
            # This website does not have system information - set to Null
            output = self.output_template.copy()
            output['source'] = name
            output['system'] = self.null

            # Populate vessel name
            # soup.title.text = 'NORDLINK - Passenger/Ro-Ro Cargo Ship - Details and current position IMO 9336256 MMSI 266252000 | Vessels | VesselFinder'
            try:
                output['name'] = soup.title.text.split('-')[0].strip()
            except IndexError:
                output['name'] = self.null

            for line in info_lines:

                if line.has_attr('itemprop'):

                    # Class
                    # <span class="value" itemprop="type">Passenger/Ro-Ro Cargo Ship</span>
                    if line.attrs['itemprop'] == 'type':
                        try:
                            output['class'] = line.text
                        except IndexError:
                            output['class'] = self.null

                    # Callsign
                    # <span class="value" itemprop="callsign">PJDZ</span>
                    elif line.attrs['itemprop'] == 'callsign':
                        try:
                            output['callsign'] = line.text
                        except IndexError:
                            output['callsign'] = self.null

                    # IMO Number
                    # <span class="value" itemprop="imoNumber">N/A</span>
                    elif line.attrs['itemprop'] == 'imoNumber':
                        try:
                            output['imo'] = line.text
                        except IndexError:
                            output['imo'] = self.null

                    # Flag
                    # <span class="value" itemprop="type">Passenger/Ro-Ro Cargo Ship</span>
                    elif line.attrs['itemprop'] == 'flag':
                        try:
                            output['flag'] = line.text
                        except IndexError:
                            output['flag'] = self.null

                    # MMSI
                    # <span class="value" itemprop="productID MMSI">266252000</span>
                    elif line.attrs['itemprop'] == 'productID MMSI':
                        try:
                            output['mmsi'] = line.text
                        except IndexError:
                            output['mmsi'] = self.null

            output = output.copy()

            # Normalize VesselFinder null values to user specified null values
            for k, v in output.copy().iteritems():
                if v == 'N/A':
                    output[k] = self.null

        soup = None
        return output

    #/* ----------------------------------------------------------------------- */#
    #/*     Define fleetmon() method
    #/* ----------------------------------------------------------------------- */#

    def fleetmon(self, **kwargs):

        """
        Get vessel information from the public FleetMON API

            https://www.fleetmon.com/faq/public_api


        Kwargs:

            name (str): Included in output in 'source' key
                [default: FleetMON]

            headers (dict): Request header
                [default: {'User-agent': self.user_agent}]

            api_user (str): FleetMON username with access to public API
                [default: None]

            api_key (str): API key for api_user
                [default: None]

            base_url (str): Base API URL - should never need to be specified
                [default: https://www.fleetmon.com/api/p/personal-v1/vesselurl/]

            callsign (bool): Specify whether or additional scraping should
                be performed in order to obtain the callsign
                [default: False]


        Returns:

            Failure: None

            Success: A dictionary containing the following vessel information:

                {
                    'name': 'NORDLINK',
                    'class': 'RoRo ship',
                    'callsign': 'SJPW',
                    'imo': '9336256',
                    'flag': 'Sweden',
                    'system': None,
                    'mmsi': '266252000',
                    'source': 'VesselFinder
                }

            Fields that cannot be collected are set to the user specified null value
            which defaults to None.

            NOTE: The 'system' field cannot be collected


        Raises:

            requests.exceptions.*: Exceptions can be raised by the initial request
                but none are suppressed

            ValueError: If api_user/key is None or f a BeautifulSoup parse returns
                unexpected results
        """

        name = kwargs.get('name', 'FleetMON')
        api_key = kwargs.get('api_key', None)
        api_user = kwargs.get('api_user', None)
        base_url = kwargs.get('base_url', 'https://www.fleetmon.com/api/p/personal-v1/vesselurl/')
        headers = kwargs.get('headers', {'User-agent': self.user_agent})
        get_callsign = kwargs.get('callsign', False)
        timeout = kwargs.get('timeout', self.timeout)
        if api_key is None or api_user is None:
            raise ValueError("api_key/user cannot be None")
        if base_url[-1] != '/':
            base_url += '/'

        # Construct API call URL and make request
        call_url = base_url + '?username=%s&api_key=%s&format=json&mmsi=%s' % (api_user, api_key, self.mmsi)
        response = requests.get(call_url, timeout=timeout, headers=headers)
        response.raise_for_status()
        json_response = json.loads(response.text)
        response.close()

        # FleetMON doesn't have the vessel - return nothing
        if 'error' in json_response or json_response['meta']['total_count'] is 0:
            output = None

        # API returned multiple results which means an imperfect match - can't do anything
        elif json_response['meta']['total_count'] > 1:
            # TODO: Investigate this condition - will FleetMON ever return more than 1?
            raise ValueError("FleetMON API returned > 1 result")

        # Got everything - parse
        else:

            # Populate info from the API response
            output = self.output_template.copy()
            output['system'] = self.null  # Doesn't specify AIS vs. VMS vs. etc.
            output['source'] = name
            output['name'] = unicode(json_response['objects'][0].get('name', self.null))
            output['class'] = unicode(json_response['objects'][0].get('type', self.null))
            output['imo'] = unicode(json_response['objects'][0].get('imo', self.null))
            output['flag'] = unicode(json_response['objects'][0].get('flag', self.null))
            output['mmsi'] = unicode(json_response['objects'][0].get('mmsi', self.null))
            # Callsign defaults to null through the template

            # Attempt to get the callsign by scraping the vessel info page
            if get_callsign:

                # Rather than pass the exception error to the parent process, just return the output
                # Raising an exception would fail this entire MMSI just because the callsign could not
                # be retrieved.  The API response has the most important information and should be
                # returned regardless
                try:
                    response = requests.get(json_response['objects'][0]['publicurl'],
                                            timeout=self.timeout, headers=headers)
                except Exception:
                    return output

                # Load soup
                soup = BeautifulSoup(response.text)
                response.close()
                vessel_info_table = soup.find_all('table', {'id': 'vessel-related', 'class': 'datasheet'})

                # Could not extract the table containing vessel information from the vessel info page
                # Return what was collected from the API
                if not vessel_info_table:
                    soup = None
                    return output

                else:

                    # Search through the table elements to find 'Callsign:' - the next cell has the right value
                    # The FleetMON uses some unicode characters as null values in the table and the decode()
                    # attempts to find these.  A failed decode means that the cell is null.
                    for row in vessel_info_table[0].find_all('tr'):
                        cells = row.find_all('td')
                        for i, c in enumerate(cells):
                            if c.label:
                                if c.text.strip() == 'Callsign:':
                                    try:
                                        value = cells[i + 1].text.strip().decode()
                                    except UnicodeEncodeError:
                                        value = self.null
                                    output['callsign'] = value

        soup = None
        return output


#/* ======================================================================= */#
#/*     Define auto_scrape() function
#/* ======================================================================= */#

def auto_scrape(mmsi_scraper, _get_options=False, **kwargs):

    """
    Keep trying a scraper until a result is returned or all retries are exhausted.


    Args:
        scraper (MMSI.*): An instance of the MMSI() class and scraper to be called


    Kwargs:

        retry (int): Maximum number of times the scraper should be called before
            a failure is assumed.  If the scraper returns a non-None result before
            the max is reached, the scrape is considered a success and subsequent
            attempts are not made.

        pause (int|float|str|unicode): Amount of time to wait between each scrape
            attempt.  Set to 'random' to pick a value between pause_min/max

        pause_min (int|float): Min value for use with pause='random'

        pause_max (int|float): Max value for use with pause='random'

        stream (obj w/ .write()): An open file object or object supporting
            a .write() method.  All exceptions are caught and sent to this
            stream.

        stream_prefix (str): Prefix for all stream writes - used for indentation
            in the batch scripts

        skip_scraper (list|tuple|"str,str,..."): List of scrapers to skip

        keep_scraper (list|tuple|"str,str,..."): List of scrapers to call


    Returns:

        Output from the input scraper


    Raises:

        ValueError: For all invalid arguments
    """

    # Used in documentation building
    _auto_options = {
        'retry': "(int): Number of retry attempt for each scraper",
        'pause': "(int|float|'random'): Num of seconds to pause between each scrape",
        'pause_min': "(int): Min number of seconds to pause when pause=random",
        'pause_max': "(int): Max number of seconds to pause when pause=random",
        'keep_scraper': "(list|tuple|str,str): Only run listed scrapers",
        'skip_scraper': "(list|tuple|str,str): Skip listed scrapers",
        'scraper_order': "(list|tuple|str,str): The order in which all scrapers are processed"
    }
    if _get_options:
        return _auto_options

    # TODO: Investigate the option of performing scrapes for ALL scrapers simultaneously with the multiprocessing
    #   Would drastically speed up failed vessels, but would slow all scrapes to the speed of the slowest scraper

    global DEFAULT_RETRY
    global DEFAULT_PAUSE
    global DEFAULT_PAUSE_MIN
    global DEFAULT_PAUSE_MAX

    # Parse arguments
    retry = kwargs.get('retry', DEFAULT_RETRY)
    stream = kwargs.get('stream', sys.stdout)
    pause = kwargs.get('pause', DEFAULT_PAUSE)
    pause_min = kwargs.get('pause_min', DEFAULT_PAUSE_MIN)
    pause_max = kwargs.get('pause_max', DEFAULT_PAUSE_MAX)
    stream_prefix = kwargs.get('stream_prefix', '')
    keep_scraper = kwargs.get('keep_scraper', None)
    skip_scraper = kwargs.get('skip_scraper', None)
    all_scraper_options = kwargs.get('scraper_options', {})
    verbose = kwargs.get('verbose', False)
    scraper_order = kwargs.get('scraper_order', MMSI.scraper_order)
    if isinstance(scraper_order, (str, unicode)):
        scraper_order = scraper_order.split(',')
    if isinstance(keep_scraper, (str, unicode)):
        keep_scraper = keep_scraper.split(',')
    if isinstance(skip_scraper, (str, unicode)):
        skip_scraper = skip_scraper.split(',')

    result = None
    for name in scraper_order:

        # The last pass got a result - no need to continue
        if result is not None:
            break

        # Figure out if this scraper should actually be done
        do_scrape = False
        if keep_scraper is None and skip_scraper is None:
            do_scrape = True
        elif keep_scraper is not None and name in keep_scraper:
            do_scrape = True
        elif skip_scraper is not None and name not in skip_scraper:
            do_scrape = True

        # Get this scraper's options
        scraper_options = all_scraper_options.get(name, {})

        # Only attempt scrape if the skip/keep conditions say so
        if do_scrape:
            for attempt_num in range(1, retry + 1):

                # Pause to prevent bombarding the server with traffic from the same IP
                if pause == 'random':
                    time.sleep(random.randint(pause_min, pause_max))
                else:
                    time.sleep(pause)

                # Successful scrape - no need to continue trying
                try:
                    result = getattr(mmsi_scraper, name)(**scraper_options)
                    if result is not None:
                        break

                # Failed scrape
                except Exception, e:

                    # Alert of total failure
                    if attempt_num is retry:
                        status_string = "MMSI: %s  %s  attempt %s/%s: %s - FAILED\n"

                    # Alert of failed attempt
                    else:
                        status_string = "MMSI: %s  %s  attempt %s/%s: %s\n"

                    if verbose:
                        stream.write(stream_prefix + status_string % (mmsi_scraper.mmsi, name,
                                                                      attempt_num, retry, e))

    return result
