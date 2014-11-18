#!/bin/bash

while read mmsi; do
    bq -q  --format=csv query -n 10000  "select mmsi, latitude, longitude, timestamp, score, cog, sog from [ProcessRun.2013_all_1_3__2014_09_24] where mmsi=$mmsi limit 10000" | ./csv2kml.py - tracks/$mmsi-2013.kml
    bq -q  --format=csv query -n 10000  "select mmsi, latitude, longitude, timestamp, score, cog, sog from [Global_20k_2012.processed_1_4_2] where mmsi=$mmsi limit 10000" | ./csv2kml.py - tracks/$mmsi-2012.kml

done <$1


#bq -q  --format=csv query -n 10000  "select mmsi, latitude, longitude, timestamp, score, cog, sog from [ProcessRun.2013_all_1_3__2014_09_24] where mmsi=$1 limit 10000" | ./csv2kml.py - $1-2013.kml
