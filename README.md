pelagos-data
============

Data management tools for the Pelagos project

[![Build Status](https://travis-ci.org/SkyTruth/pelagos-data.svg?branch=pipeline)](https://travis-ci.org/SkyTruth/pelagos-data)



### Adding a layer to regions.sqlite ###

         > ogr2ogr ../data/regions/regions.sqlite -append NOAA-MPA-8.shp -progress -f SQLite -lco OVERWRITE=YES -nlt POLYGON
