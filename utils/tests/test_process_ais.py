import unittest2
import calendar
from datetime import datetime
import StringIO
import csv
import os

from .. import process_ais


class ModelTransformTest(unittest2.TestCase):

    def _open_fixture(self, filename):
        return open(os.path.join(os.path.dirname(__file__), 'fixtures', filename), 'r')

    def test_transform_file(self):
        csv_in = self._open_fixture('process_ais_input_v1_3.csv')
        actual_output = StringIO.StringIO()
        expected_output = self._open_fixture('process_ais_output_v1_3.csv')
        transform = process_ais.Transform()
        transform.transform_file(csv_in, actual_output)
        actual_output.seek(0)
        for expected in expected_output:
            actual = actual_output.readline()
            self.assertEqual(expected, actual)

        self.assertDictEqual(transform.stats, {'bad score':1, 'bad latitude':1, 'bad longitude':1})
