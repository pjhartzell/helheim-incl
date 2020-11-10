# Helheim Inclination 
A script to apply scanner inclination data to ATLAS North and South point clouds. Vertical repeatability improvement is in the 50% range, with extreme examples showing up to 90% improvement.


## 1. Problem
Point clouds from the same scanner do not vertically align on stationary (exposed rock) surfaces. The alignment differences are greater at longer ranges, suggesting non-stationary scanner orientation.


## 2. Mitigation Approaches
The general concept is to apply the roll and pitch angles that are supplied by the scanner inclination sensors to each point cloud. We have experimented with rigid point cloud rotations, based on single mean roll and pitch values, and non-rigid point cloud transformations, where each point is rotated according to the closest roll and pitch values in time. The roll and pitch signals are low-passed prior to the non-rigid transformations. Two examples of raw and low-passed roll and pitch signals from ATLAS South scans are shown below.

_180804_010156 - Filtered Roll and Pitch (0100 local time)_
![](images/inclination/filteredrollpitch-south-180804_010156.png)

_180804_190154 - Filtered Roll and Pitch (1900 local time)_
![](images/inclination/filteredrollpitch-south-180804_190154.png)

In order of typical magnitude, these roll and pitch inclination signals consist of the following:

- Static scanner inclination (the single roll and pitch values that would exist if the scanner inclination did not change during the course of the scan),
- A cyclical (period = 360°) systematic inclination sensor error.
- Temporal inclination changes the scanner is experiencing within a scan.

Given the presence of cyclical sensor error, applying the non-rigid transformation will introduce a vertical "wave" into the point cloud. Single rigid rotations, on the other hand, ignore intra-scan inclination changes. In either case, the inclination must be applied to point clouds in the SOCS system. Doing so, however, invalidates the SOP matrix, since the SOP matrix itself is based on a scan with similar inclination values. Thus, applying the SOP matrix after applying the inclination data results in a (roughly) double application of the inclination data.

We address the problem of "double" inclination application by removing either the mean or modeled cyclical component of the scan used to solve the SOP matrix, which is the scan used in the MSA registration. This produces much better alignment in the final UTM coordinate system between overlapping North and South scan data on stationary (exposed rock) surfaces. Qualitatively, it appears that a non-rigid transformation using inclination signals that have had the modeled cyclical component of the MSA registration scan removed produce the most improvement in relative inter-scan alignment throughout the point cloud. Note that the cyclical component is modeled with a sine wave having a period of phi=360°, where phi is the horizontal scan angle. An example of the cyclical model (from the MSA scan corresponding to the filtered signals shown above) and this model subsequently removed from the roll and pitch signals shown above are given below.

_180731_010159 - MSA Scan Modeled Roll and Pitch_
![](images/inclination/modeledrollpitch-south-180731_010159-msascan.png)

_180804_010156 - Model Removed, Filtered Roll and Pitch (Scan is at same time of day as MSA scan)_
![](images/inclination/modelremoved-filteredrollpitch-south-180804_010156.png)

_180804_190154 - Model Removed, Filtered Roll and Pitch (Scan is at different time of day as MSA scan)_
![](images/inclination/modelremoved-filteredrollpitch-south-180804_190154.png)

Notes:
- The cyclical model fit is degraded by any intra-scan motion present in the SOP MSA scans. It appears that the early morning (0100 local time) scans tend to be well-behaved with respect to the cyclical model. Thus, these 0100 local time scans should be preferred for future MSA adjustments, as they may suffer less intra-scan motion than late day scans.
- The low-pass filter size is based on prior work with the Arapahoe Basin data. Qualitative inspection suggests it may be over-smoothing the signal, thus reducing the effectiveness of the warp correction. However, finding the optimal filter size is likely an empirical exercise and may also depend on environmental conditions (e.g., wind speed). For now, the filter is believed to be conservative, and we prefer to err on the side of not injecting noise into the point cloud.


## 3. Use
You will need a directory containing MTA'd RXP files.

1. Build and install Pete's [rivlib-utils](https://github.com/gadomski/rivlib-utils) on your machine. Change the `false` argument to `true` on line #10 in the source file `inclination.cpp` before building. This changes the timestamps from internal time to GPS time.
2. Copy the `rxp2incl.sh` script to your MTA directory and run to extract inclination data from the RXP files. Text files containing time, roll, and pitch (units are GPS time seconds and degrees) will be saved into the RXP directory with "-incl" appended to the source RXP filenames.
2. Copy the `rxp2laz.sh` script to your MTA directory and run to extract and save point cloud data from the MTA RXP files. You will need PDAL with the RXP reader plugin.
3. Edit the user input at the top of the `main.py` script and run to apply the inclination data to the point cloud data. New point cloud LAZ files will be create with appropriate filenames. You can choose to do one or more of the following:
    - Not apply any inclination data.
    - Warp the point clouds with the inclination data.
    - Warp the point clouds with mean-removed inclination data.
    - Warp the point clouds with trend-removed inclination data, where the "trend" is the cyclical model.
    - Rigidly rotate the point clouds using the mean of the mean-removed inclination data.
    - Optionally georeference the output of the above adjustments to UTM.


## 4. Sample Result Data
You can download sample data from [here](https://uofh-my.sharepoint.com/:f:/g/personal/pjhartze_cougarnet_uh_edu/En7uPV7ur-1GrKyoPuz479YBZl0B2Fs6f8Lm1URzX-fHSw?e=l4ujnh). 


## 5. Typical Sample Profiles

- ATLAS South data, projected to UTM
- Green = Current; Red = MSA model removed, warped
- Note that the proposed method does not eliminate the vertical discrepancy; it is only able to remove a large portion of it.

_180804 - Exposed Rock - All 4 Scans_
![](/images/profiles/180804-4scans-1.png)


_180804 - Exposed Rock - All 4 Scans_
![](/images/profiles/180804-4scans-2.png)


