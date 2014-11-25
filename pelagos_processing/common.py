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
Objects needed by multiple modules
"""


import json


#/* ======================================================================= */#
#/*     Define string2type() function
#/* ======================================================================= */#

def string2type(i_val):

    """
    Convert an input string to a Python type


    Example:

        JSON: '{"woo": [1, 2, "3"]}' --> {'woo': [1, 2, '3']}
        Integer: "1"    -->     1
        Float: "1.23"   -->     1.23
        None: "None"    -->     None
        True: "True"    -->     True
        False: "False"  -->     False
        String: "Word"  -->     "Word"

        None, True, and False are not case sensitive
    """

    # Force value to Python type
    try:
        return int(i_val)
    except ValueError:
        try:
            return float(i_val)
        except ValueError:
            if i_val.lower() == 'true':
                return True
            elif i_val.lower() == 'false':
                return False
            elif i_val.lower() == 'none':
                return None
            else:
                try:
                    return json.loads(i_val)
                except ValueError:
                    return i_val


#/* ======================================================================= */#
#/*     Define increment_stat() function
#/* ======================================================================= */#

def increment_stat(container, stat):

    """
    Simple wrapper to keep track of how many times an event happened.

    If the specified state does not appear in the container it will be added
    and given a value of 1.  If it does appear the value will be iterated.


    Args:

        container (dict): Dictionary where stats are/will be kept

        stat (str|unicode): Name of key to iterate


    Returns:

        Nothing
    """

    if stat in container:
        container[stat] += 1
    else:
        container[stat] = 1
