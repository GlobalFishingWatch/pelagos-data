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
Required to allow easier access to test data
"""


from os.path import abspath, dirname
from os import sep


#/* ======================================================================= */#
#/*     Provide easy access to specific test datasets
#/* ======================================================================= */#

marine_traffic_20k = abspath(dirname(__file__)) + sep + 'data' + 'MarineTraffic_20k.csv'
vessel_finder_20k = abspath(dirname(__file__)) + sep + 'data' + 'VesselFinder_20k.csv'
fleetmon_20k = abspath(dirname(__file__)) + sep + 'data' + 'FleetMON_20k.csv'
unclassified_mmsi_20k = abspath(dirname(__file__)) + sep + 'data' + 'unclassified_mmsi_20k.csv'
