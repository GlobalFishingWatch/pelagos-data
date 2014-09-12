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
Utilities required for collecting vessel information from a variety of sources
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
DEFAULT_USER_AGENT = 'Mozilla/30.0'
DEFAULT_SCRAPER_OFIELDS = ['name', 'class', 'callsign', 'imo', 'flag', 'system', 'mmsi', 'source']
DEFAULT_OUTPUT_TEMPLATE = {i: None for i in DEFAULT_SCRAPER_OFIELDS}


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

    def __init__(self, mmsi, user_agent=None, null=None, timeout=DEFAULT_TIMEOUT, **kwargs):

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

        # Scraper specific options
        self.fleetmon_api_user = kwargs.get('fleetmon_api_user', None)
        self.fleetmon_api_key = kwargs.get('fleetmon_api_key', None)

        # Output template for scrapers to dump info into
        self.output_template = {i: self.null for i in self.ofields}

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
                            output['class'] = line.text.strip()
                        except IndexError:
                            output['class'] = self.null

                    # Callsign
                    # <span class="value" itemprop="callsign">PJDZ</span>
                    elif line.attrs['itemprop'] == 'callsign':
                        try:
                            output['callsign'] = line.text.strip()
                        except IndexError:
                            output['callsign'] = self.null

                    # IMO Number
                    # <span class="value" itemprop="imoNumber">N/A</span>
                    elif line.attrs['itemprop'] == 'imoNumber':
                        try:
                            output['imo'] = line.text.strip()
                        except IndexError:
                            output['imo'] = self.null

                    # Flag
                    # <span class="value" itemprop="type">Passenger/Ro-Ro Cargo Ship</span>
                    elif line.attrs['itemprop'] == 'flag':
                        try:
                            output['flag'] = line.text.strip()
                        except IndexError:
                            output['flag'] = self.null

                    # MMSI
                    # <span class="value" itemprop="productID MMSI">266252000</span>
                    elif line.attrs['itemprop'] == 'productID MMSI':
                        try:
                            output['mmsi'] = line.text.strip()
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
                    'source': 'FleetMON'
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
        api_key = kwargs.get('api_key', self.fleetmon_api_key)
        api_user = kwargs.get('api_user', self.fleetmon_api_user)
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
            output['name'] = json_response['objects'][0].get('name', self.null)
            output['class'] = json_response['objects'][0].get('type', self.null)
            output['imo'] = json_response['objects'][0].get('imo', self.null)
            output['flag'] = json_response['objects'][0].get('flag', self.null)
            output['mmsi'] = json_response['objects'][0].get('mmsi', self.null)
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

        # FleetMON's API returns IMO and MMSI values stored as int's but all other scrapers return str/unicode
        # Normalize to string type
        for k, v in output.copy().iteritems():
            if v != self.null:
                output[k] = unicode(v)
            else:
                output[k] = v

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
                     a failure is assumed.  If the scraper returns a non-None
                     result before the max is reached, the scrape is considered
                     a success and subsequent attempts are not made.
        pause (int|float|str|unicode): Amount of time to wait between each scrape
                                       attempt.  Set to 'random' to pick a value
                                       between pause_min/max
        pause_min (int|float): Min value for use with pause='random'
        pause_max (int|float): Max value for use with pause='random'
        stream (file): An open file object or object supporting a .write() method.
                       All exceptions are caught and sent to this stream.
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

                # Attempt a scrape
                try:
                    result = getattr(mmsi_scraper, name)(**scraper_options)

                    # Successful scrape - no need to continue trying
                    if result is not None:
                        break

                # Failed scrape
                except Exception, e:

                    # Alert of total failure
                    status_string = "MMSI: %s  %s  attempt %s/%s: %s\n"
                    if attempt_num is retry:
                        status_string += "FAILED\n"

                    if verbose:
                        stream.write(stream_prefix + status_string % (mmsi_scraper.mmsi, name,
                                                                      attempt_num, retry, e))

    return result


#/* ======================================================================= */#
#/*     Define gp_blacklist_vessel() function
#/* ======================================================================= */#

def gp_blacklist_vessel(url, get_scraper_options=False, get_output_fields=False, **kwargs):

    """
    Given a URL to a blacklisted Greenpeace vessel collect available information


    Args:

        url     (str): URL to a blacklisted vessel's page


    Kwargs:

        headers         (dict): Header to use for HTTP request
                                [default: {'User-agent': self.user_agent}]
        timeout         (int): Number of seconds to wait before assuming the
                               HTTP request is a failure
                               [default: 30]
        null            (anything): Value to use when no value could be scraped
                                    [default: None]
        scraper_name    (anything): Name of this scraper
                                    [default: GreenpeaceBlacklist]

    Field Map:

        Website                     Output Dict

        Blacklisted In              blacklisted_in
        IRCS                        callsign
        Vessel Type                 class
        Controller Country/Region   controller_region
        Fishing Number              fishing_number
        Flag                        flag
        IMO                         imo
        Links                       links
        Satcom                      mmsi
        Name                        name
        Notes                       notes
        Owner Company               owner_company
        Previous IRCS               previous_callsign
        Previous Companies          previous_companies
        Previous Flags              previous_flags
        Previous Names              previous_names
        Vessel Length               vessel_length
        date                        Some fields contain the date updated
                                    so if the date is present in at least
                                    one field, the first occurrence is returned
        url                         Input URL
        source                      Name of scraper
        system                      AIS vs. VMS vs. etc. - Currently null for
                                    this scraper


    Sample Output:

        {
            'blacklisted_in': 'Greenpeace\nReason for blacklisting: <TRUNCATED>',
            'callsign': 'Unknown',
            'class': 'Driftnetter',
            'controller_region': 'Tunisia',
            'date': '2007-06-20',
            'fishing_number': None,
            'flag': 'Tunisia',
            'imo': 'Unknown',
            'links': 'http://www.greenpeace.org/raw/content/ <TRUNCATED>',
            'mmsi': None,
            'name': 'Ahmed Helmi',
            'notes': 'On the morning of 20 June 2007, a dozen <TRUNCATED>',
            'owner_company': None,
            'previous_callsign': None,
            'previous_companies': None,
            'previous_flags': None,
            'previous_names': None,
            'source': None,
            'system': None,
            'url': 'http://blacklist.greenpeace.org//1/vessel/ <TRUNCATED>',
            'vessel_length': None
        }
    """

    global DEFAULT_TIMEOUT
    global DEFAULT_USER_AGENT
    global DEFAULT_SCRAPER_OFIELDS

    # Parse arguments
    headers = kwargs.get('headers', {'User-agent': DEFAULT_USER_AGENT})
    timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
    null = kwargs.get('null', None)
    scraper_name = kwargs.get('scraper_name', 'GreenpeaceBlacklist')

    # Output containers
    output = {i: null for i in DEFAULT_SCRAPER_OFIELDS + [
        'previous_names', 'blacklisted_in', 'notes', 'previous_flags',
        'owner_company', 'previous_companies', 'previous_callsign', 'vessel_length',
        'controller_region', 'fishing_number', 'links', 'date', 'url'
    ]}

    if get_scraper_options:
        return gp_blacklist(get_scraper_options=True)

    if get_output_fields:
        return output.keys()

    # Make request, check for errors and load into BeautifulSoup
    response = requests.get(url, timeout=timeout, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text)
    response.close()

    # Extract the table containing the vessel attributes
    table = soup.find_all('table', {'id': 'detail'})
    if len(table) is not 1:
        soup = None
        raise ValueError("Unexpected BeautifulSoup result - found multiple vessel tables")

    # Add known information
    output['url'] = url
    output['source'] = scraper_name

    # Extract information
    soup = None
    table_rows = table[0].find_all('tr')
    for idx, tr in enumerate(table_rows):

        txt = tr.text.strip().split(':')[0]
        _val = tr.find('td').text.strip()
        val = tr.find('td').text.rsplit('(')[0].encode('utf-8').strip()
        if output['date'] is None:
            date = _val.split('(')
            if len(date) > 1:
                output['date'] = date[1].replace(')', '')
        
        if txt == 'Name':
            output['name'] = val

        elif txt == 'Previous Name(s)':
            output['previous_names'] = val

        elif txt == 'Blacklisted In':
            output['blacklisted_in'] = val

        elif txt == 'Notes':
            output['notes'] = val

        elif txt == 'Flag':
            output['flag'] = val

        elif txt == 'Previous Flags':
            output['previous_flags'] = val

        elif txt == 'Owner Company':
            output['owner_company'] = val

        elif txt == 'Previous Companies':
            output['previous_companies'] = val

        elif txt == 'IRCS':
            output['callsign'] = val

        elif txt == 'Previous IRCS':
            output['previous_callsign'] = val

        elif txt == 'IMO Number':
            output['imo'] = val

        elif txt == 'Vessel Type':
            output['class'] = val

        elif txt == 'Vessel Length':
            output['vessel_length'] = val

        elif txt == 'Controller Country/Region':
            output['controller_region'] = val

        elif txt == 'Satcom Number':
            output['mmsi'] = val

        elif txt == 'Fishing Number':
            output['fishing_number'] = val

        elif txt == 'Links':
            output['links'] = val

    # Make empty strings null
    for k, v in output.copy().iteritems():
        if not v:
            v = null
        output[k] = v

    return output


#/* ======================================================================= */#
#/*     Define gp_blacklist() function
#/* ======================================================================= */#

def gp_blacklist(get_scraper_options=False, get_output_fields=False, **kwargs):

    """
    Given a URL to a blacklisted Greenpeace vessel collect available information


    Args:

        url     (str): URL to a blacklisted vessel's page


    Kwargs:

        headers         (dict): Header to use for HTTP request
                                [default: {'User-agent': self.user_agent}]

        timeout         (int): Number of seconds to wait before assuming the
                               HTTP request is a failure
                               [default: 30]

        null            (anything): Value to use when no value could be scraped
                                    [default: None]

        scraper_name    (anything): Name of this scraper
                                    [default: GreenpeaceBlacklist]


    Field Map:

        Website                     Output Dict

        Blacklisted In              blacklisted_in
        IRCS                        callsign
        Vessel Type                 class
        Controller Country/Region   controller_region
        Fishing Number              fishing_number
        Flag                        flag
        IMO                         imo
        Links                       links
        Satcom                      mmsi
        Name                        name
        Notes                       notes
        Owner Company               owner_company
        Previous IRCS               previous_callsign
        Previous Companies          previous_companies
        Previous Flags              previous_flags
        Previous Names              previous_names
        Vessel Length               vessel_length
        date                        Some fields contain the date updated
                                    so if the date is present in at least
                                    one field, the first occurrence is returned
        url                         Input URL
        source                      Name of scraper
        system                      AIS vs. VMS vs. etc. - Currently null for
                                    this scraper


    Sample Output:

        A list of output from gp_blacklist_vessel()

        [
            {
                'name': 'Vessel1',
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: <TRUNCATED>',
                'callsign': 'Unknown',
                'class': 'Driftnetter',
                'controller_region': 'Tunisia',
                'date': '2007-06-20',
                ...
            },
            {
                'name': 'Vessel2',
                'blacklisted_in': 'Greenpeace\nReason for blacklisting: <TRUNCATED>',
                'callsign': 'Unknown',
                'class': 'Driftnetter',
                'controller_region': 'Tunisia',
                'date': '2007-06-20',
                ...
            },
            ...
        ]


        With return_urls=True

            [
                'http://blacklist.greenpeace.org//1/vessel/show/169-ahmed-helmi',
                'http://blacklist.greenpeace.org/1/vessel/show/43-lung-soon-888',
                'http://blacklist.greenpeace.org/1/vessel/show/111-viarsa-i-scrapped'
            ]
    """

    global DEFAULT_TIMEOUT
    global DEFAULT_USER_AGENT

    _scraper_options = {
        'url': "(str): Page containing the list of all vessels",
        'timeout': "(int): Number of seconds to wait until a scrape request is considered a failure",
        'headers': "(dict): Header parameter for each scrape request",
        'base_vessel_url': "(str): Base URL to which the vessel path is appended"
    }
    if get_scraper_options:
        return _scraper_options

    if get_output_fields:
        return gp_blacklist_vessel(None, get_output_fields=True)

    # Parse arguments
    url = kwargs.get('url', 'http://blacklist.greenpeace.org/1/vessel/list?gp_blacklist=1&startswith=A-Z')
    base_vessel_url = kwargs.get('base_vessel_url', 'http://blacklist.greenpeace.org')
    headers = kwargs.get('headers', {'User-agent': DEFAULT_USER_AGENT})
    timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
    return_urls = kwargs.get('return_urls', False)

    # The inbound URL's all have a leading '/' so remove it from the base_url
    if base_vessel_url[-1] == '/':
        base_vessel_url = base_vessel_url[:-1]

    # Make request, check for errors and load into BeautifulSoup
    response = requests.get(url, timeout=timeout, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text)

    # Vessels are referenced internally by a UID which is just their row number in the site's table
    # Get a list of vessels web pages to scrape
    table = soup.find_all('table', {'id': 'blacklist', 'class': 'vessels'})
    if len(table) is not 1:
        soup = None
        raise ValueError("Unexpected BeautifulSoup result - found multiple vessel tables")
    links = [base_vessel_url + link['href'] for link in table[0].find_all('a', href=True)]

    if return_urls:
        return links
    else:
        return [gp_blacklist_vessel(url) for url in links]
