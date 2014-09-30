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
Configfile utilities
"""


from __future__ import unicode_literals

from datetime import datetime
import getpass
import os
import subprocess
import sys

import config


class Controller(object):

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __init__(self, params):

        # Load configfile
        if isinstance(params, dict):
            self.params = params
        elif isinstance(params, config.ConfigParser):
            self.params = config.as_dict(params)
        elif isinstance(params, (str, unicode)):
            self.params = config.as_dict(config.from_path(params))
        else:
            raise ValueError("Invalid params - must be a dict, ConfigParser, or path to configfile")

        _run = 'run'
        _name = 'name'
        self.name = self.params[_run][_name]
        self.version = str(self.params['run']['version'])

        if self.name is None:
            raise ValueError("Entry '%s' in section '%s' is None - can't construct fullname" % (_name, _run))

        self.fullname = self.params['run'].get(
            'fullname', '-'.join(
                [
                    getpass.getuser(),
                    datetime.utcnow().strftime('%Y%m%d'),
                    self.name,
                    'v' + self.version
                ]
            )
        )

        self.run_dir = os.path.join(self.params['run']['process_runs'], self.fullname)
        self.raw = self.params['run']['raw']
        self.bqschema = self.params['run']['bqschema']
        self.bqtable = self.params['run']['bqtable']
        self.regions = self.params['run']['regions']
        self.steps = self.params['run']['steps'].split(',')
        self.shutdown = self.params['run']['shutdown']

    @staticmethod
    def _exists(check_path):

        check_path = check_path.strip()

        # Local file
        if len(check_path) <= 5 or check_path[:5] != 'gs://' or check_path[:7] == 'file://':
            return os.path.exists(check_path if 'file://' not in check_path else check_path[:7])

        # Google Cloud Storage file
        else:
            # TODO: Migrate to gslib + boto
            p = subprocess.Popen(['gsutil', 'ls', check_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = p.communicate()
            if output and not err:
                return True
            elif not output and err:
                return False
            else:
                raise IOError("Could not determine if path exists: %s" % check_path)

    @staticmethod
    def _bq_obj_exists(obj_path):

        p = subprocess.Popen(['gsutil', 'ls', obj_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if output and not err:
            return True
        elif not output and err:
            return False
        else:
            raise IOError("Could not determine if BigQuery object exists: %s" % obj_path)

    @staticmethod
    def _onpath(util):
        for item in sys.path:
            if Controller._exists(os.path.join(item, util)):
                return True
        return False

    @staticmethod
    def _gce_instance_exists(instance_name):
        p = subprocess.Popen(['gcloud', 'compute', 'instances', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if output and not err:
            return instance_name in output
        else:
            raise IOError("Could not determine if GCE instance exists: %s" % instance_name)

    def get(self, config_option):
        if '.' in config_option:
            section, option = config_option.split('.')
            return self.params[section][option]
        elif hasattr(self, config_option):
            return getattr(self, config_option)

    def validate(self):

        # Some of the utilities are used to see if other stuff exists
        for util_name in self.steps:
            util = self.params['processing'][util_name + '_util']
            if os.sep in util and not Controller._exists(util) and not Controller._onpath(util):
                raise IOError("Can't find utility: %s" % util)

        # Validate names
        if ' ' in self.name:
            raise IOError("Run name cannot contain spaces")

        # Check if an instance with the same name already exists
        if Controller._gce_instance_exists(self.fullname):
            raise IOError("GCE instance already exists: %s" % self.fullname)

        # Make sure the target run directory and BigQuery table doesn't exist
        if self._exists(self.run_dir):
            raise IOError("Target run directory already exists: %s" % self.run_dir)
        if self._bq_obj_exists(self.bqtable):
            raise IOError("Target BigQuery table already exists: %s" % self.bqtable)

        # Validate required options
        if not self._exists(self.raw):
            raise IOError("Can't find raw input: %s" % self.raw)
        if not self._exists(self.bqschema):
            raise IOError("Can't find BigQuery schema: %s" % self.bqschema)
        if not self._exists(self.regions):
            raise IOError("Can't find regions: %s" % self.regions)

        return True
