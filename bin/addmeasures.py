import csv
import sys
import math
import operator
import itertools
import datetime
import rolling_measures
import global_measures

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


def unmangle(row):
    res = {}
    for key, value in row.iteritems():
        if isinstance(value, datetime.datetime):
            value = value.strftime("%s")
        elif isinstance(value, datetime.timedelta):
            value = str(value.total_seconds())
        elif isinstance(value, (float, int)):
            value = str(value)
        res[key] = value
    return res

distances_to_port = global_measures.PixelReader('distance-from-port-2km/distance-from-port.tif')

inkeys = ['mmsi','longitude','latitude','timestamp','score','navstat','hdg','rot','cog','sog']
outkeys = ["distance_to_port", "new_score"]

windowSize = datetime.timedelta(seconds=args['window'])

def addMeasures(infile, outfile):
    with open(infile) as startIn:
        with open(infile) as endIn:
            with open(outfile, "w") as out:
                stats = rolling_measures.Stats({
                        "cogstddev": rolling_measures.Stat("cog", rolling_measures.StdDev),
                        "sogstddev": rolling_measures.Stat("sog", rolling_measures.StdDev),
                        "cogavg": rolling_measures.Stat("cog", rolling_measures.Avg),
                        "sogavg": rolling_measures.Stat("sog", rolling_measures.Avg),
                        "latitudeavg": rolling_measures.Stat("latitude", rolling_measures.Avg),
                        "longitudeavg": rolling_measures.Stat("longitude", rolling_measures.Avg),
                        "pos": rolling_measures.StatSum(rolling_measures.Stat("latitude", rolling_measures.StdDev),
                                                        rolling_measures.Stat("longitude", rolling_measures.StdDev))
                        })

                diffkeys = ['longitude','latitude','timestamp','hdg','rot','cog','sog']
                diffdiffkeys = [key + "_diff" for key in diffkeys]

                startIn = iter(mangle(csv.DictReader(startIn, inkeys)))
                endIn = iter(mangle(csv.DictReader(endIn, inkeys)))

                out = csv.DictWriter(out, inkeys + diffdiffkeys + stats.fieldmap.keys() + outkeys, 'ignore')
                out.writeheader()

                start = None
                last = None
                for end in endIn:
                    if last is None: last = end
                    end.update({key + "_diff": abs(end[key] - last[key]) for key in diffkeys})

                    end['distance_to_port'] = distances_to_port.read(end['longitude'], end['latitude']) / 1852.0 # Convert from meters to nautical miles 

                    stats.add(end)
                    while not start or end['timestamp'] - start['timestamp'] > windowSize:
                        if start:
                            stats.remove(start)
                        start = startIn.next()
                    s = stats.get()
                    # Knots...
                    s['pos'] = (s['pos'] * 60) / (windowSize.total_seconds() / 60 / 60)
                    # Normalize to "normal" vessel speed
                    s['pos'] /= 17.0
                    s['pos'] = min(1.0, s['pos'])
                    end.update(s)

                    end['new_score'] = (end['cogstddev'] + end['sogstddev'] + end['sogavg']) / 3.0
                    
                    out.writerow(unmangle(end))
                    last = end


try:
    addMeasures(*files)
except Exception, e:
    print e
    import pdb
    sys.last_traceback = sys.exc_info()[2]
    pdb.pm()
