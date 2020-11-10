import os
from incl import *


# ------------------------------------------------------------------------------
# Directory of data to be processed:
#   LAZ files generated from the MTA'd RXP files; Must be in SOCS
#   TXT files generated from the MTA'd RXP files
# The directory contents must be associated with only one SOP matrix.
data_dir = "/mnt/e/ATLAS/south_200501-200515/mta"
# Required supporting data
sop_file = "/mnt/e/ATLAS/registration/sop_pop/ATLAS-South-201908-SOP.dat"
pop_file = "/mnt/e/ATLAS/registration/sop_pop/ATLAS-POP.dat"
msa_pnts_file = "/mnt/e/ATLAS/registration/scans/msa/south/190804_153929-mta.laz"
msa_incl_file = "/mnt/e/ATLAS/registration/scans/msa/south/190804_153929-mta-incl.txt"
# ------------------------------------------------------------------------------


# Only need to compute the SOP MSA modeled inclination once
msa_it, msa_roll, msa_pitch = get_incl(msa_incl_file)
msa_t, msa_x, msa_y, _ = get_pnts(msa_pnts_file)
msa_phi = get_phi(msa_it, msa_t, msa_x, msa_y)
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
    t, x, y, z = get_pnts(laz_file)
    it, roll, pitch = get_incl(incl_file)

    # Adjust points
    tr_warp_adj(t, x, y, z, it, roll, pitch,
                msa_roll_params, msa_pitch_params,
                sop_file, pop_file, data_dir, basename)
