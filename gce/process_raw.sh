#!/bin/bash

# pull down the raw data file
gsutil cp gs://analyze-data/raw/atw2_20k-raw.csv.gz .

# Process
gunzip -c atw2_20k-raw.csv.gz | /usr/local/src/pelagos-data/utils/process_ais.py | gzip -c > atw2_20k-processed.csv.gz

# upload it
gsutil cp atw2_20k-processed.csv.gz gs://analyze-data/processed


# load into BigQuery
bq load --skip_leading_rows=1 --max_bad_records=100 \
    Global_20k_2012.processed_1_3 gs://analyze-data/processed/atw2_20k-processed.csv.gz \
    /usr/local/src/pelagos-data/schema/scored-ais-processed-schema-1.3.json

# Regionate test
cd /usr/local/src/pelagos-data/
gunzip -c ./data/sample_ais/processed_1_3_10k_points.csv.gz | \
    ./utils/regionate.py ./data/regions/regions.sqlite | \
    gzip -c > ~/regionated_1_3_10k_points.jsin.gz

# Regionate
gunzip -c atw2_20k-processed.csv.gz |
    /usr/local/src/pelagos-data/utils/regionate.py
    /usr/local/src/pelagos-data/data/regions/region.sqlite |
    gzip -c  > atw2_20k-region.json.gz

# upload it
gsutil cp atw2_20k-region.json.gz gs://analyze-data/processed/


# load into bigquery
bq load --source_format=NEWLINE_DELIMITED_JSON \
    Scratch.atw2_20k_region_dev2 gs://analyze-data/processed/atw2_20k-region-dev2.json.gz \
    /usr/local/src/pelagos-data/schema/scored-ais-processed-schema-1.4.json

cat > my-new-tileset-name.json <<EOF
{
  "name": "Global-20k-2012",
  "workspace_template": "pelagos-2012-template.json",
  "params": {
    "table": "Global_20k_2012.processed_1_4_1"
  },
  "generator": "bqtile.TileGenerator"
}
EOF

gsutil cp -a public-read my-new-tileset-name.json gs://skytruth-pelagos-redhog/tilesets
