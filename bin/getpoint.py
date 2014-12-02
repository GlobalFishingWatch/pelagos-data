import global_measures

r = global_measures.PixelReader('distance-from-port-2km/distance-from-port.tif')
for lat in xrange(-90, 90):
    for lng in xrange(-180, 180):
        val = r.read(lng, lat)
        print "%s,%s = %s" % (lng, lat, val)
