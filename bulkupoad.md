#Bulk Upload to App Engine Data Store

This tells how we are uploading data into the data store on GAE.

Say your model looks like this:

### vesselinfo.py

    class VesselInfo(ndb.Model):
        source = ndb.StringProperty()
        sourceid = ndb.StringProperty()
        datetime = ndb.DateTimeProperty()
        mmsi = ndb.StringProperty()
        imo = ndb.StringProperty()
        callsign = ndb.StringProperty()
        vesselname = ndb.StringProperty()
        vesselclass = ndb.StringProperty()
        flagstate = ndb.StringProperty()

Add this to app.yaml in the GAE app

### app.yaml
    builtins:
    - remote_api: on

Create a local yaml file with the load configuration.  Here's an example
### vesselinfo-bulkloader.yaml
    python_preamble:
    - import: base64
    - import: re
    - import: google.appengine.ext.bulkload.transform
    - import: google.appengine.ext.bulkload.bulkloader_wizard
    - import: google.appengine.ext.db
    - import: google.appengine.api.datastore
    - import: google.appengine.api.users

    transformers:
    - kind: VesselInfo
      connector: csv
      connector_options:
        encoding: utf-8
      property_map:
        - property: __key__
          external_name: series
          export_transform: datastore.Key.name
        - property: mmsi
          external_name: mmsi
        - property: source
          external_name: source
        - property: sourceid
          external_name: sourceid
        - property: datetime
          external_name: datetime
          import_transform: transform.import_date_time('%Y-%m-%d')
        - property: callsign
          external_name: callsign
        - property: vesselclass
          external_name: vesselclass
        - property: vesselname
          external_name: vesselname
        - property: flagstate
          external_name: flagstate
        - property: imo
          external_name: imo

Get some data to upload.

### vesselinfo_test.csv
    series,mmsi,source,sourceid,datetime,callsign,vesselclass,flagstate,imo,vesselname
    19946,245688000,MarineTraffic.com,245688000,2014-07-24,PBBO,Dredger,Netherlands,,SIMSON
    19945,247323600,MarineTraffic.com,247323600,2014-07-24,IJES2,Sailing vessel,Italy,9606247,OHANA
    20000,371,MarineTraffic.com,371,2014-07-24,3FCZ6,Tug,,,GEO CASPIAN
    19995,2331,MarineTraffic.com,2331,2014-07-24,E.T,Wing In Grnd,,,MBIGUA
    103,503005000,Global_20k_AIS,503005000,2012-07-01,,,,,
    95,503000026,Global_20k_AIS,503000026,2012-07-01,,,,,
    94,503000005,Global_20k_AIS,503000005,2012-07-01,,,,,
    93,503000004,Global_20k_AIS,503000004,2012-07-01,,,,,


Do the load.  This connects to the local dev server

    appcfg.py upload_data --config_file=./vesselinfo-bulkloader.yaml \
    --filename=./vesselinfo_test.csv --kind=VesselInfo \
    --num_threads=4 --url=http://localhost:8080/_ah/remote_api  \
    --rps_limit=500 --email=admin@admin.com


### NOTES

* It has to connect with a user that has admin priviledges.  For the local dev server any valid email address will do.
* If you omit the email param it will prompt you.
* Since we are specifying the key explicitly, if you re-run the import with the same data, it will overwrite instead of creating duplicates







