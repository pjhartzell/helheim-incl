#!/bin/bash
for filename in /mnt/e/ATLAS/south_200501-200515/rxp/mta/*.rxp
do
	echo "Converting $filename to ${filename%.rxp}.laz"
	pdal translate "$filename" "${filename%.rxp}.laz" 
done
