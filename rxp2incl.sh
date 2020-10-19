#!/bin/bash
for filename in /mnt/e/ATLAS/south_200501-200515/rxp/mta/*.rxp
do
	echo "Extracting inclination from $filename. Saving to ${filename%.rxp}-incl.txt"
	ri-inclination "$filename" > "${filename%.rxp}-incl.txt" 
done
