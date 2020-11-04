import numpy as np
import matplotlib.pyplot as plt
from incl import *


# ------------------------------------------------------------------------------
# Directory containing the LAZ and inclination TXT files
data_dir = "/mnt/e/ATLAS/north_180801-180807/mta"
sop_file = "/mnt/e/ATLAS/registration/sop_pop/ATLAS-North-201807-SOP.dat"
pop_file = "/mnt/e/ATLAS/registration/sop_pop/ATLAS-POP.dat"
reg_incl_file = "/mnt/e/ATLAS/registration/scans/msa/north/180730_223212-mta-incl.txt"

# Option to plot the inclination data for each file
plot = False

# Inclination application options. Any option set to 'True' will result in a LAZ
# file for that option being created. So you can produce LAZ files for all three 
# options by setting them all to 'True'.
#   'no_adjust' = Do not apply inclination data.
#   'warp' = Apply each inclination reading to points closest in time.
#   'mr_warp' = Remove registration mean inclinations before warp.
no_adjust = True
warp = True
mr_warp = True

# Georeference to UTM (True) or leave in SOCS (False)
georef = True
# ------------------------------------------------------------------------------


laz_files = [f for f in os.listdir(data_dir) if f.endswith(".laz")]
for laz_file in laz_files:
    # MTA'd, unfiltered LAZ file in SOCS
    laz_file = data_dir + "/" + laz_file
    print("Applying inclination to {}".format(laz_file))

    # Corresponding file of inclination roll and pitch in degrees
    root, ext = os.path.splitext(os.path.basename(laz_file))
    incl_file = data_dir + "/" + root + "-incl.txt"

    # Read in the point and inclination data
    pt, x, y, z = get_pnts(laz_file)
    it, roll, pitch = get_incl(incl_file)

    # Save unadjusted points?
    if no_adjust:
        if georef:
            xg, yg, zg = sop_pop_cloud(x, y, z, sop_file)
            xg, yg, zg = sop_pop_cloud(xg, yg, zg, pop_file)
            outfilename = data_dir + "/" + root + "-utm.laz"
            save_utm(outfilename, pt, xg, yg, zg)
        else:
            outfilename = data_dir + "/" + root + "-socs.laz"
            save_pnts(outfilename, pt, x, y, z)

    # Filter the inclination data
    filtered_roll = filter_incl(roll, kernel_length=101)
    filtered_pitch = filter_incl(pitch, kernel_length=101)

    #  Plot raw and filtered inclination data, if desired
    if plot:
        plot_incl_time(it, roll, pitch, filtered_roll, filtered_pitch)

    # Save the filtered roll and pitch inclinations
    outfilename = data_dir + "/" + root + "-incl-filtered.txt"
    np.savetxt(
        outfilename,
        np.column_stack((it, filtered_roll, filtered_pitch)),
        "%0.4f",
        delimiter=',',
        header="Time,FilteredRoll,FilteredPitch"
    )

    # Warp points?
    if warp:
        # Apply inclination
        xw, yw, zw = warp_cloud(pt, x, y, z, it, filtered_roll, filtered_pitch)
        # Save warped points
        if georef:
            xg, yg, zg = sop_pop_cloud(xw, yw, zw, sop_file)
            xg, yg, zg = sop_pop_cloud(xg, yg, zg, pop_file)
            outfilename = data_dir + "/" + root + "-warped-utm.laz"
            save_utm(outfilename, pt, xg, yg, zg)
        else:
            outfilename = data_dir + "/" + root + "-warped-socs.laz"
            save_pnts(outfilename, pt, xw, yw, zw)

    # Warp after removing mean registration inclinations?
    if mr_warp:
        # Remove MSA registration scan mean inclination
        mr_filtered_roll, mr_filtered_pitch = remove_reg_mean_incl(
            filtered_roll, filtered_pitch, reg_incl_file
        )
        # Apply inclination
        xw, yw, zw = warp_cloud(
            pt, x, y, z,
            it, mr_filtered_roll, mr_filtered_pitch
        )
        # Save warped points
        if georef:
            xg, yg, zg = sop_pop_cloud(xw, yw, zw, sop_file)
            xg, yg, zg = sop_pop_cloud(xg, yg, zg, pop_file)
            outfilename = data_dir + "/" + root + "-regmeanrem-warped-utm.laz"
            save_utm(outfilename, pt, xg, yg, zg)
        else:
            outfilename = data_dir + "/" + root + "-regmeanrem-warped-socs.laz"
            save_pnts(outfilename, pt, xw, yw, zw)
