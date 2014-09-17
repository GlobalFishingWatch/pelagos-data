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


import json
import os
import sys

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


#/* ======================================================================= */#
#/*     Define string2type() function
#/* ======================================================================= */#

def string2type(i_val):

    """
    Convert an input string to a Python type
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
#/*     Define config2ict() function
#/* ======================================================================= */#

def config2dict(cfg_parser_obj):

    """
    Convert an instance of ConfigParser to a dictionary
    """

    output = {}
    for section in cfg_parser_obj.sections():
        output[section] = {k: string2type(v) for k, v in cfg_parser_obj.items(section)}

    return output.copy()


#/* ======================================================================= */#
#/*     Define dict2config() function
#/* ======================================================================= */#

def dict2config(config_dict):

    """
    Convert a dictionary to a ConfigParser object
    """

    config = ConfigParser()
    for section in config_dict.keys():
        config.add_section(section)
        for k, v in config_dict[section].iteritems():
            config.set(section, k, v)

    return config


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

def main(args):

    print("Setting up for Travis CI...")
    kwargs = {}
    for arg in args:
        try:
            option, value = arg.split('=')
            kwargs[option.lower()] = value
        except ValueError:
            print("ERROR: Invalid argument: %s" % arg)
            return 1

    configfile = kwargs.get('configfile', 'Config.cfg')

    try:
        fleetmon_user = kwargs.get('fleetmon_user', os.environ['fleetmon_user'])
        fleetmon_key = kwargs.get('fleetmon_key', os.environ['fleetmon_key'])
    except KeyError:
        print("ERROR: fleetmon_user or fleetmon_key could not be found - set an environment variable or set via the commandline")
        return 1

    load_config = ConfigParser()
    load_config.read(configfile)
    config_content = config2dict(load_config)

    # Set up FleetMON by populating API user and key
    if config_content['FleetMON']['user'] is None:
        config_content['FleetMON']['user'] = fleetmon_user
    if config_content['FleetMON']['key'] is None:
        config_content['FleetMON']['key'] = fleetmon_key

    # Write the configfile back out
    write_config = dict2config(config_content)
    with open(configfile, 'w') as f:
        write_config.write(f)

    # Cleanup
    print("Done")
    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Remove script name and give the rest to main
    sys.exit(main(sys.argv[1:]))
