#!/bin/bash

if [ -z "$2" ]
  then
    echo "Usage: regionate.sh gs://folder/input.csv.gz gs://folder/output.json.gz  [NUMBER OF PROCESSES]"
    exit 1
fi

if [ -z "$3" ]
then
  N=$(nproc)
else
  N=$3
fi

IN=$1
TEMP='temp'
IN_CSV="$TEMP/in.csv"
OUT=$2

echo "Regionating $IN to $OUT"
echo "Using $N parallel processes"
echo ""
echo "$(date)" "Cleaning up"
rm -rf $TEMP
mkdir $TEMP

echo "Unpacking input"
gsutil cp $IN - | gunzip -c > $IN_CSV

echo ""
echo "Splitting input"
# skip the first one because it will get the header from 
# the source file when it gets the first split section
for (( i=2; i<=$N; i++ ))
do
  head -n 1 $IN_CSV > $TEMP/in-$i
done

for (( i=1; i<=$N; i++ ))
do
  ( split -n r/$i/$N -u  $IN_CSV >> $TEMP/in-$i ) &
done

wait 

echo ""
echo "$(date)" "Regionating"

for (( i=1; i<=$N; i++ ))
do
  ( 
  echo "$(date)" "Regionate $i Start"
  /usr/local/src/pelagos-data/utils/regionate.py ./regions.sqlite $TEMP/in-$i $TEMP/out-$i 

  echo "$(date)" "Regionate $i Complete" 
  ) &
done

wait

echo "$(date) Merging results into $OUT"

## NB: This does not work for files larger than 2GB
## Gives error:  Failure: size does not fit in an int.
# cat $TEMP/out-* | gzip -c | gsutil cp - $OUT

# Need to do this instead
cat $TEMP/out-* | gzip -c > regionate.json.gz
gsutil cp regionate.json.gz $OUT

echo ""
echo "$(date)" "Run Complete"

rm -rf $TEMP
