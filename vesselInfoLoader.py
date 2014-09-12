#! /usr/bin/env python

import MySQLdb
import contextlib
import sys
import csv
import hashlib
import datetime
import json

@contextlib.contextmanager
def connection(**config):
    db = MySQLdb.connect(**config)
    try:
        yield db
    finally:
        db.close()

def dictreader(cur):
    cols = None
    for row in cur:
        if cols is None:
            cols = [dsc[0] for dsc in cur.description]
        yield dict(zip(cols, row))

def getdict(cur):
    for row in dictreader(cur):
        return row
    return None

def parseargs(rawargs):
    options = {}
    args = []
    for arg in rawargs:
        if arg.startswith('--'):
            arg = arg[2:]
            if '=' in arg:
                arg, value = arg.split("=", 1)
                options[arg] = value
            else:
                options[arg] = True
        else:
            args.append(arg)
    return options, args

def convert(type, value):
    try:
        return type(value)
    except:
        return None

def comparerows(row1, row2):
    exclude = set(("recordid", "last_checked", "datetime"))
    cols = set().union(row1.iterkeys(),
                       row2.iterkeys()) - exclude
    for col in cols:
        if row1[col] != convert(type(row1[col]), row2[col]):
            print "row1.%s != row2.%s: %s != %s" % (col, col, row1[col], row2[col])
            return False
    return True

builtincols = set(("recordid",
                   "source",
                   "sourceid",
                   "datetime",
                   "mmsi",
                   "imo",
                   "callsign",
                   "vesselname",
                   "vesselclass",
                   "draught",
                   "to_bow",
                   "to_port",
                   "to_starboard",
                   "to_stern",
                   "flag",
                   "last_checked"))

def collapserow(row):
    builtins = dict((name, value)
                    for (name, value) in row.iteritems()
                    if name in builtincols)
    extras = dict((name, value)
                  for (name, value) in row.iteritems()
                  if name not in builtincols)
    builtins['info'] = json.dumps(extras)
    return builtins

def expandrow(row):
    row = dict(row)
    row.update(json.loads(row.pop('info')))
    return row

options, args = parseargs(sys.argv[1:])
dbargs = dict((name, value) for (name, value) in options.iteritems()
              if name in ('host', 'db', 'user', 'passwd'))

if not options or 'help' in options:
    print """Loads vessel records into the Pelagos vessel info database,
doing deduplication / change tracking on the fly.


Usage:

vesselInfoLoader.py \\
  --host=1.2.3.4 \\
  --db=mydb \\
  --user=root \\
  --passwd=guessthatifyoucan \\
  --input=vesselInfoLoader.example.csv

"""
    sys.exit(1)

with connection(**dbargs) as db:
    with contextlib.closing(db.cursor()) as cur:

        with open(options['input']) as f:
            c = csv.DictReader(f)

            for idx, row in enumerate(c):
                if not row.get('sourceid', None):
                    row['sourceid'] = hashlib.sha224('\n'.join(
                            row.get(name, '')
                            for name in ('mmsi', 'imo', 'callsign', 'shipname')
                            )).hexdigest()

                if 'datetime' not in row:
                    row['datetime'] = datetime.datetime.now()

                cur.execute('select * from vessel_records where source = %(source)s and sourceid = %(sourceid)s order by last_checked desc limit 1', row)
                existing = getdict(cur)
                
                if existing and comparerows(expandrow(existing), row):
                    row['recordid'] = existing['recordid']
                    cur.execute('update vessel_records set last_checked=%(datetime)s where recordid = %(recordid)s', row)
                else:
                    cur.execute("""
                        insert into vessel_records (
                          source,
                          sourceid,
                          datetime,
                          mmsi,
                          imo,
                          callsign,
                          vesselname,
                          vesselclass,
                          draught,
                          to_bow,
                          to_port,
                          to_starboard,
                          to_stern,
                          flag,
                          info,
                          last_checked
                        ) select
                          %(source)s,
                          %(sourceid)s,
                          %(datetime)s,
                          %(mmsi)s,
                          %(imo)s,
                          %(callsign)s,
                          %(vesselname)s,
                          %(vesselclass)s,
                          %(draught)s,
                          %(to_bow)s,
                          %(to_port)s,
                          %(to_starboard)s,
                          %(to_stern)s,
                          %(flag)s,
                          %(info)s,
                          %(datetime)s
                    """, collapserow(row))
                if idx % 50 == 0:
                    cur.execute('commit')
            cur.execute('commit')
