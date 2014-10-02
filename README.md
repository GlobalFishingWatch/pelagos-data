pelagos-data
============

Data management tools for the Pelagos project

[![Build Status](https://travis-ci.org/SkyTruth/pelagos-data.svg?branch=pipeline)](https://travis-ci.org/SkyTruth/pelagos-data)



### Adding a layer to regions.sqlite ###

         > ogr2ogr ../data/regions/regions.sqlite -append NOAA-MPA-8.shp -progress -f SQLite -lco OVERWRITE=YES -nlt POLYGON


REGIONS HOWTO
=============

To create a  regions sqlite file to use with regionate.py:

Put a shapefile for each layer into a folder called "regions"

Create the sqlite file with:

    ogr2ogr -f Sqlite -dsco SPATIALITE=YES -nlt polygon regions-2014-10-01.sqlite regions

Replace the date in the file name with today's date.