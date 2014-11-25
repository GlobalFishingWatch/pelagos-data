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
Data for unittests
"""


import os


#/* ======================================================================= */#
#/*     Provide easy access to specific test datasets
#/* ======================================================================= */#

_data_dir = os.path.abspath(os.path.dirname(__file__))

process_ais_input14 = os.path.join(_data_dir, 'process_ais_input_v14.csv')
process_ais_output14 = os.path.join(_data_dir, 'process_ais_output_v14.csv')

sample_config = os.path.join(_data_dir, 'Test-Config.cfg')

cat1 = os.path.join(_data_dir, 'cat1.csv')
cat2 = os.path.join(_data_dir, 'cat2.csv')
cat3 = os.path.join(_data_dir, 'cat3.csv')
cat4 = os.path.join(_data_dir, 'cat4.csv')
