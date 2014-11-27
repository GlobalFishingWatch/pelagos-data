import csv
import numpy
import datetime

class namedArray(object):
    def __init__(self, cols, arr):
        self.cols = cols
        self.arr = arr
    def __getattr__(self, name):
        return self.arr[self.cols.index(name)]
    def __getitem__(self, *arg, **kw):
        return type(self)(self.cols, self.arr.__getitem__(*arg, **kw))



def load(filename):
    def mangle(rows):
        for row in rows:
            orig = dict(row)
            for key, value in row.iteritems():
                if key == 'mmsi':
                    pass
                else:
                    row[key] = float(value)
            row['_'] = orig
            yield row

    rows = 0
    with open(filename) as infile:
        for row in infile:
            rows += 1
    rows -= 1 # header

    with open(filename) as infile:
        infile = csv.DictReader(infile)
        cols = infile.fieldnames
        arr = numpy.zeros((len(cols), rows))
        for rowidx, row in enumerate(mangle(infile)):
            for colidx, col in enumerate(cols):
                if isinstance(row[col], float):
                    arr[colidx,rowidx] = row[col]

    return namedArray(cols, arr)
