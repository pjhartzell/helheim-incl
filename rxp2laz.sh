#!/bin/bash
for filename in *.rxp
do
	echo "Converting $filename to ${filename%.rxp}.laz"
	pdal translate "$filename" "${filename%.rxp}.laz" 
done
