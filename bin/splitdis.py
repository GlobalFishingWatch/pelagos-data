import csv
import sys
import math
import operator
import itertools
import datetime
import rolling_measures
import pyproj
geod = pyproj.Geod(ellps="WGS84")

args = {
    "window": 60*60
}
files = []
for arg in sys.argv[1:]:
    if arg.startswith("--"):
        arg = arg[2:]
        if '=' in arg:
            arg, value = arg.split("=", 1)
            args[arg] = value
        else:
            args[arg] = True
    else:
        files.append(arg)

args['window'] = float(args['window'])

def mangle(rows):
    for row in rows:
        for key, value in row.iteritems():
            if key == 'mmsi':
                pass
            elif key == 'timestamp':
                row[key] = datetime.datetime.fromtimestamp(int(row[key]))
            else:
                row[key] = float(value)

        # Normalize
        row['score'] = row['score'] / 5.0
        row['hdg'] = row['hdg'] / 360.0
        row['cog'] = row['cog'] / 360.0
        row['sog'] = 1.0 - min(1.0, row['sog'] / 17.0)

        yield row


class Bin(object):
    bins = []
    filename = files[0].replace(".csv", "")
    binid = 0

    def __init__(self):
        cls = type(self)
        self.file = open("%s.path-%s.csv" % (cls.filename, cls.binid), "w")
        cls.binid += 1
        self.writer = csv.DictWriter(self.file, inkeys, 'ignore')
        self.row = None
        self.bins.append(self)

    def close(self):
        self.file.close()
        self.bins.remove(self)

    def add_to_bin(self, row):
        if self.row is not None:
            distance = geod.inv(row['longitude'], row['latitude'],
                                self.row['longitude'], self.row['latitude'])[2] / 1852.0
            timespan = (row['timestamp'] - self.row['timestamp']).total_seconds() / (60 * 60)

            if timespan > discontinuity_time:
                self.close()
                return False

            if ((timespan > 0.0
                 and distance / timespan > discontinuity_speed)
                or (timespan == 0.0
                    and distance > 0)):
                return False
        self.row = row
        self.writer.writerow(row)
        return True

    @classmethod
    def add(cls, row):
        for bin in cls.bins:
            if bin.add_to_bin(row):
                return
        Bin().add_to_bin(row)

inkeys = ['mmsi','longitude','latitude','timestamp','score','navstat','hdg','rot','cog','sog']

discontinuity_time = 72
discontinuity_speed = 100 # knots

bins = []
current_bin = None

with open(files[0]) as infile:
    infile = iter(mangle(csv.DictReader(infile, inkeys)))
    for row in infile:
        Bin.add(row)
for bin in Bin.bins:
    bin.close()
