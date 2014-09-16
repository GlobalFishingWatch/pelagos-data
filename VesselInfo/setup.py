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
Setup script for VesselInfo
"""


from glob import glob

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import vessel_info


setup(
    name='VesselInfo',
    version=vessel_info.__version__,
    author=vessel_info.__author__,
    author_email=vessel_info.__author_email__,
    description=vessel_info.__doc__,
    long_description=vessel_info.__doc__,
    license=vessel_info.__license__,
    url=vessel_info.__source__,
    packages=[
        'vessel_info',
        'vessel_info.utils',
        'vessel_info.tests',
        'vessel_info.tests.testdata'
    ],
    scripts=glob('bin/*.py'),
    include_package_data=True,
    classifiers=[
        'Topic :: Terminals',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ]
)
