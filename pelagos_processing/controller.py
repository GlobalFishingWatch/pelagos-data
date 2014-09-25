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

        self.name = self.params['run']['name']
        self.version = str(self.params['run']['version'])

        if self.name is None:
            raise ValueError("Entry 'name' in section 'run' is None - can't construct fullname")

        self.fullname = '-'.join([datetime.utcnow().strftime('%Y-%m-%d_%H:%m'), getpass.getuser(), self.name, 'v' + self.version])

        self.raw = self.params['run']['raw']
        self.bqschema = self.params['run']['bqschema']
        self.bqtable = self.params['run']['bqtable']
        self.regions = self.params['run']['regions']
        self.steps = self.params['run']['steps'].split(',')
        self.shutdown = self.params['run']['shutdown']

    @staticmethod
    def _exists(path):

        path = path.strip()

        # Local file
        if len(path) <= 5 or path[:5] != 'gs://' or path[:7] == 'file://':
            return os.path.exists(path if 'file://' not in path else path[:7])

        # Google Cloud Storage file
        else:
            p = subprocess.Popen(['gsutil', 'ls', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = p.communicate()
            if output.split('\n') >= 1:
                return True
            else:
                return False

    @staticmethod
    def _onpath(util):
        for item in sys.path:
            if Controller._exists(os.path.join(item, util)):
                return True
        return False

    def validate(self):

        if not self._exists(self.raw):
            raise IOError("Can't find raw input: %s" % self.raw)
        if not self._exists(self.bqschema):
            raise IOError("Can't find Big Query schema: %s" % self.bqschema)
        if not self._exists(self.regions):
            raise IOError("Can't find regions: %s" % self.regions)
        for util_name in self.steps:
            util = self.params[util_name]['util']
            if os.sep in util and not Controller._exists(util) and not Controller._onpath(util):
                raise IOError("Can't find utility: %s" % util)

        return True

    def go(self):
        pass
