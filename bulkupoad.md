#Bulk Upload to App Engine Data Store

This tells how we are uploading data into the data store on GAE.

Add this to app.yaml in the GAE app

    builtins:
    - remote_api: on

Create a local yaml file with the load configuration.  Here's an example

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
        - property: vesselid
          external_name: series
          import_transform: int
        - property: mmsi
          external_name: mmsi
          import_transform: int

Get some data to upload.  Example:
    id,mmsi
    1,477897100
    2,477897700
    3,477897800
    4,477898200


Do the load.  This connects to the local dev server

    appcfg.py upload_data --config_file=../Scratch/bulkloader.yaml \
    --filename=../Scratch//bulkloadtest.csv --kind=VesselInfo \
    --num_threads=4 --url=http://localhost:8080/_ah/remote_api \
    --has_header --rps_limit=500 --email=admin@admin.com \
    --log_file=../temp/bulkupload.log  --db_filename=../temp/bulkupload_progress.db

### NOTES

* It has to connect with a user that has admin priviledges.  For the local dev server any valid email address will do.  If you omit the email param it wil prompt you.






