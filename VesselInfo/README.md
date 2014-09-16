VesselInfo
==========

Tools for compiling marine vessel information

[![Build Status](https://travis-ci.org/SkyTruth/pelagos-data.svg?branch=vesselinfo)](https://travis-ci.org/SkyTruth/pelagos-data)


Installing
==========

        $ git clone https://github.com/SkyTruth/pelagos-data
        $ cd pelagos-data/VesselInfo
        
Open the `Config.cfg` file and populate the `user` and `key` values with information from FleetMON.
        
        $ pip install -r requirements.txt
        $ ./run_tests.py
        $ pip install . --upgrade


Commandline Utilities
=====================

For more information use one of the help flags, which are accessible via `<UTILITY> --help-info`


mmsi2info.py
------------

Collect information about vessels listed in an input CSV from a variety of sources

## Example commands

        mmsi2info.py --help-info

        mmsi2info.py \
          -ao scraper_order=marine_traffic \
          -ao pause=1 \
          Input_MMSI.csv \
          Output.csv

compare_scrape.py
-----------------

Compare output from `mmsi2info.py` from multiple sources to determine which ones produce differing results

