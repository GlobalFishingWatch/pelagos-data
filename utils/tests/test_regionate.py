import unittest2
import calendar
from datetime import datetime
import StringIO
import csv
import os

from .. import regionate


class RegionateTest(unittest2.TestCase):

    def _get_fixture_path(self, filename):
        return os.path.join(os.path.dirname(__file__), 'fixtures', filename)

    def _open_fixture(self, filename):
        return open(self._get_fixture_path(filename), 'r')

    def test_regionate_pipa(self):
        csv_in = self._open_fixture('regionate_input.csv')
        actual_output = StringIO.StringIO()
        expected_output = self._open_fixture('regionate_output_pipa.json')
        args={'POLY_LAYER': self._get_fixture_path('pipa/pipa.shp'),
              '--attribute':'regionid',
              '--layername': None}
        regionate.regionate(csv_in, actual_output, args)
        actual_output.seek(0)
        for expected in expected_output:
            actual = actual_output.readline()
            self.assertEqual(expected, actual)

    def test_regionate_ocean(self):
        csv_in = self._open_fixture('regionate_input.csv')
        actual_output = StringIO.StringIO()
        expected_output = self._open_fixture('regionate_output_ocean.json')
        args={'POLY_LAYER': self._get_fixture_path('ocean-region-10km.sqlite'),
              '--attribute': 'regionid',
              '--layername': 'ocean2'}
        regionate.regionate(csv_in, actual_output, args)
        actual_output.seek(0)
        for expected in expected_output:
            actual = actual_output.readline()
            self.assertEqual(expected, actual)