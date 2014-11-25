import csv
import sys
import math
import operator
import itertools
import datetime
import rolling_measures

args = {
    "maxdist": 60*60,
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

inkeys = ['mmsi','longitude','latitude','timestamp','score','navstat','hdg','rot','cog','sog']
outkeys = []

windowSize = datetime.timedelta(60*60)

def addMeasures(infile, outfile):
    with open(infile) as startIn:
        with open(infile) as endIn:
            with open(outfile, "w") as out:
                stats = rolling_measures.Stats({
                        "cogstddev": rolling_measures.Stat("cog", rolling_measures.StdDev),
                        "sogstddev": rolling_measures.Stat("sog", rolling_measures.StdDev),
                        "avgsog": rolling_measures.Stat("sog", rolling_measures.Avg),
                        "pos": rolling_measures.StatSum(rolling_measures.Stat("latitude", rolling_measures.StdDev),
                                                        rolling_measures.Stat("longitude", rolling_measures.StdDev))
                        })

                startIn = iter(mangle(csv.DictReader(startIn, inkeys)))
                endIn = iter(mangle(csv.DictReader(endIn, inkeys)))
                out = csv.DictWriter(out, inkeys + stats.fieldmap.keys(), 'ignore')
                out.writeheader()

                start = None
                for end in endIn:
                    stats.add(end)
                    while not start or end['timestamp'] - start['timestamp'] > windowSize:
                        if start:
                            stats.remove(start)
                        start = startIn.next()
                    row = end['_']
                    row.update(stats.get())
                    out.writerow(row)


try:
    addMeasures(*files)
except Exception, e:
    print e
    import pdb
    sys.last_traceback = sys.exc_info()[2]
    pdb.pm()
