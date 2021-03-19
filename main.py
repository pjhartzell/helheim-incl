"""Helheim TLS diurnal motion correction script.

WHAT IT DOES:
-------------
1. Estimates the "base" trend of the scanner inclination angles with respect to
the horizontal SOCS scan angle (phi) using the inclination angles contained in
the annual MSA scan data.
2. Removes the estimated base trend from the inclination angles of each 
subsequent scan to generate residual (detrended) inclination angles. The
residual angles are smoothed to remove high-frequency noise. These smoothed
residual inclination angles are an estimate of the diurnal roll and pitch motion
experienced by the the scanner.
3. Rotates each SOCS coordinate by the smoothed residual inclination angles
nearest in time to remove (to an extent) the diurnal motion. Since many
different rotations are applied to the SOCS coordinates within a single scan,
the adjustment has been termed a "warp".
4. Transforms and reprojects the adjusted (warped) SOCS points to UTM zone 24N
(ITRF2014) and saves the adjusted point cloud to a LAZ file. Also saves the 
residual (detrended) inclination angles and smoothed residual inclination angles
to separate TXT files. 
5. Optionally saves unadjusted points in UTM to an additional LAZ file. 

REQUIREMENTS & ASSUMPTIONS:
---------------------------
1. This script requires LAZ point cloud files and TXT inclination angle files for
all scans being adjusted to be contained in a single directory. The LAZ and TXT
files should be generated from MTA'd RXP files. The rxp2laz.sh and rxp2incl.sh
shell scripts will generate the LAZ and TXT files with names as expected by the 
this Python script. See the "Use" section in the readme.
2. This script assumes that all data in the directory being processed falls
within the time range of a single MSA / SOP definition. See the files in the
"support" directory for date ranges and file names associated with the MSA / SOP
definitions.
3. The path to the directory containing the LAZ and TXT inclination data files
to be processed must be entered in the "USER INPUT" section below. The paths to
the correct MSA, SOP, and POP files must also be entered in the "USER INPUT"
section below.
4. To export unadjusted points (in addition to the adjusted points), set the
"save_unadjusted" variable to True in the "USER INPUT" section below.
"""

# REQUIRED USER INPUT ----------------------------------------------------------
data_dir = "/mnt/d/ATLAS/south_190624-190628/mta"
msa_pnts_file = "/mnt/d/ATLAS/registration/scans/msa/south/180731_010159-mta.laz"
msa_incl_file = "/mnt/d/ATLAS/registration/scans/msa/south/180731_010159-mta-incl.txt"
sop_file = "/mnt/d/ATLAS/registration/sop_pop/ATLAS-South-201807-SOP.dat"
pop_file = "/mnt/d/ATLAS/registration/sop_pop/ATLAS-POP.dat"
save_unadjusted = True
# ------------------------------------------------------------------------------

import os
from incl import *

# Only need to compute the SOP MSA modeled inclination once
msa_it, msa_roll, msa_pitch = get_incl(msa_incl_file)
msa_array = get_pnts(msa_pnts_file)
msa_phi = get_phi(msa_it, msa_array["GpsTime"], msa_array["X"], msa_array["Y"])
msa_roll_params = fit_model(msa_phi, msa_roll)
msa_pitch_params = fit_model(msa_phi, msa_pitch)

# Cycle through scans
laz_files = [f for f in os.listdir(data_dir) if f.endswith(".laz")]
for laz_file in laz_files:
    # LAZ and inclination filenames
    laz_file = data_dir + "/" + laz_file
    basename, _ = os.path.splitext(os.path.basename(laz_file))
    incl_file = data_dir + "/" + basename + "-incl.txt"

    print("Processing {}".format(laz_file))

    # Read in point and inclination data
    array = get_pnts(laz_file)
    it, roll, pitch = get_incl(incl_file)

    # Optionally convert unadjusted points to UTM, save
    if save_unadjusted:
        no_adj(np.copy(array), sop_file, pop_file, data_dir, basename)

    # Adjust points, convert to UTM, save
    tr_warp_adj(array, it, roll, pitch,
                msa_roll_params, msa_pitch_params,
                sop_file, pop_file, data_dir, basename)
