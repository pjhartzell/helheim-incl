#!/bin/bash
for filename in *.rxp
do
	echo "Extracting inclination from $filename. Saving to ${filename%.rxp}-incl.txt"
	ri-inclination "$filename" > "${filename%.rxp}-incl.txt" 
done
