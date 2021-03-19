Readme file for ATLAS master matrices (10/15/2019, LeWinter)

POP:
The POP brings points into EPSG:7789, ITRF2014 geocentric.

SOP:
Each epoch for each scanner (North, South) has an associated Scanner's Own Position (SOP) matrix which combined with the POP matrix, brings points into EPSG:7789, ITRF2014 geocentric. This is necessary as each time the team serviced the systems the position of the scanner was modified. The SOP matrix naming convention is ATLAS-(Site)-(YYYYMM)-SOP.dat, where (Site) is either North or South, and (YYYYMM) is the year and month in which the new SOP applies. The below lists the scan range for each epoch.


ATLAS South SOP Data Ranges

SOP Matrix: ATLAS-South-201507-SOP.dat
Start: 150728_180208.rxp
End: 160808_18214.rxp

SOP Matrix: ATLAS-South-201608-SOP.dat
Start: 160811_173200.rxp
End: 161008_060205.rxp

SOP Matrix: ATLAS-South-201708-SOP.dat
Start: 170717_180200.rxp
End: 171207_120907.rxp

SOP Matrix: ATLAS-South-201807-SOP.dat
Start: 180727_220154.rxp
End: 190804_070155.rxp

SOP Matrix: ATLAS-South-201908-SOP.dat
Start: N/A
End: N/A


ATLAS North SOP Data Ranges

SOP Matrix: ATLAS-North-201807-SOP.dat
Start: 180731_110237.rxp
End: 180928_180240.rxp

SOP Matrix: ATLAS-North-201908-SOP.dat
Start: N/A
End: N/A
