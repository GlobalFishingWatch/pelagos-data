#!/usr/bin/env python


from os.path import *
import sys

try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr
ogr.UseExceptions()
osr.UseExceptions()


def main(args):

    dump_data = None

    for arg in args:
        if 'dump=' in arg.lower():
            dump_data = arg.split('=')[1]

    srs = osr.SpatialReference()
    srs.SetFromUserInput("EPSG:4326")

    ring_points = ((0, 0), (0, 1), (9, 1), (9, 9), (0, 9), (0, 10), (10, 10), (10, 0))
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for x, y in ring_points:
        ring.AddPoint(x, y)
    ring.CloseRings()

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AssignSpatialReference(srs)
    poly.AddGeometry(ring)

    point = ogr.Geometry(ogr.wkbPoint)
    point.AssignSpatialReference(srs)
    point.AddPoint(5, 5)

    intersect = poly.Intersects(point)
    if not intersect:
        print("GEOS is functioning properly!")
        return_val = 0
    else:
        print("WARNING: GEOS is not functioning properly.")
        return_val = 1

    if dump_data:
        definitions = [
            {
                'name': 'polygon',
                'type': ogr.wkbPolygon,
                'geometry': poly

            },
            {
                'name': 'point',
                'type': ogr.wkbPoint,
                'geometry': point
            }
        ]
        drv = ogr.GetDriverByName('ESRI Shapefile')
        ds = drv.CreateDataSource(dump_data)
        for definition in definitions:
            layer = ds.CreateLayer(definition['name'], srs, definition['type'])
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(definition['geometry'])
            layer.CreateFeature(feature)
            feature = None
            layer = None

    # Cleanup
    drv = None
    ds = None
    srs = None
    poly = None
    point = None

    return return_val

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))