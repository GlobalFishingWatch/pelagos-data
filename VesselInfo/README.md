VesselInfo
==========

Tools for compiling marine vessel information


Installing
==========

        $ git clone https://github.com/SkyTruth/pelagos-data
        $ cd pelagos-data/VesselInfo
        $ pip install -r requirements.txt
        $ pip install . --upgrade

Commandline Utilities
=====================

For more information use one of the help flags, which are accessible via `<UTILITY> --help-info`


mmsi2info.py
------------

Collect information about vessels listed in an input CSV from a variety of sources


compare_scrape.py
-----------------

Compare output from `mmsi2info.py` from multiple sources to determine which ones produce differing results
