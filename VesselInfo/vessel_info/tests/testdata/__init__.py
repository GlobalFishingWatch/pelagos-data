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
Sample and test datasets
"""


from os.path import abspath, dirname
from os import sep


#/* ======================================================================= */#
#/*     Provide easy access to specific test datasets
#/* ======================================================================= */#

_data_dir = abspath(dirname(__file__))

sample_mmsi = _data_dir + sep + '10_mmsi.csv'
unclassified_mmsi_20k = _data_dir + sep + 'data' + 'unclassified_mmsi_20k.csv'

marine_traffic_20k = _data_dir + sep + 'data' + 'MarineTraffic_20k.csv'
vessel_finder_20k = _data_dir + sep + 'data' + 'VesselFinder_20k.csv'
fleetmon_20k = _data_dir + sep + 'data' + 'FleetMON_20k.csv'

test_common_TestMain_test_standard_input1 = _data_dir + sep + 'test_common_TestMain_test_standard_input2.csv'
test_common_TestMain_test_standard_input2 = _data_dir + sep + 'test_common_TestMain_test_standard_input1.csv'
test_common_TestMain_test_standard_expected_output = _data_dir + sep + 'test_common_TestMain_test_standard_expected_output.csv'

configfile = _data_dir + sep + 'Config.cfg'
