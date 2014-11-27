import csv
import numpy
import datetime

def load(filename):
    def mangle(rows):
        for row in rows:
            orig = dict(row)
            for key, value in row.iteritems():
                if key == 'mmsi':
                    pass
                elif key == 'timestamp':
                    row[key] = datetime.datetime.fromtimestamp(int(row[key]))
                else:
                    row[key] = float(value)
            row['_'] = orig
            yield row

    cols = ['score','sog','sog_diff','sogavg','sogstddev','hdg_diff','cog_diff','cogstddev','pos']

    rows = 0
    with open(filename) as infile:
        for row in infile:
            rows += 1
    rows -= 1 # header

    arr = numpy.zeros((len(cols), rows))

    with open(filename) as infile:
        for rowidx, row in enumerate(mangle(csv.DictReader(infile))):
            for colidx, col in enumerate(cols):
                arr[colidx,rowidx] = min(1.0, abs(row[col]))

    return cols, arr

