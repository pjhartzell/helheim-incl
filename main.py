import matplotlib.pyplot as plt
from incl import *


# ------------------------------------------------------------------------------
# Directory containing the LAZ and inclination TXT files
data_dir = "/mnt/e/ATLAS/south_200501-200515/rxp/mta"
# Option to plot the inclination data for each file
plot = False
# To warp or not to warp?
# True = Apply each inclination reading to points closest in time. This is a
# non-rigid transformation (warp) of the point cloud.
# False = Apply only the mid-point inclination value to the entire point cloud.
# This is a rigid transformation of the point cloud.
warp = False
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

    # Filter the inclination data
    filtered_roll = filter_incl(roll, kernel_length=151)
    filtered_pitch = filter_incl(pitch, kernel_length=151)

    #  Plot raw and filtered inclination data, if desired
    if plot:
        plot_incl_time(it, roll, pitch, filtered_roll, filtered_pitch)

    # Transform point cloud
    if warp:
        xr, yr, zr = warp_cloud(pt, x, y, z, it, filtered_roll, filtered_pitch)
    else:
        xr, yr, zr = rotate_cloud(x, y, z, it, filtered_roll, filtered_pitch, 'mean')

    # Save the corrected SOCS point data
    root, ext = os.path.splitext(laz_file)
    if warp:
        outfilename = root + "-warped" + ext
    else:
        outfilename = root + "-rotated-mean" + ext
    save_pnts(outfilename, pt, xr, yr, zr)