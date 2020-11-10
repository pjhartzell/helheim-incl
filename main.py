import gc
import numpy as np
import matplotlib.pyplot as plt
from incl import *


# ------------------------------------------------------------------------------
# Directory containing the LAZ and inclination TXT files
data_dir = "E:/ATLAS/south_200501-200515/mta"
sop_file = "E:/ATLAS/registration/sop_pop/ATLAS-South-201908-SOP.dat"
pop_file = "E:/ATLAS/registration/sop_pop/ATLAS-POP.dat"
reg_pnts_file = "E:/ATLAS/registration/scans/msa/south/190804_153929-mta.laz"
reg_incl_file = "E:/ATLAS/registration/scans/msa/south/190804_153929-mta-incl.txt"

# Inclination application options. Any option set to 'True' will result in a LAZ
# file for that option being created.
#   'no_adjust' = Do not apply inclination data.
#   'warp' = Apply each inclination reading to points closest in time.
#   'mr_warp' = Remove registration mean inclinations before warp.
#   'tr_warp' = Remove cyclical trend in registration inclinations before warp.
#   'mr_rotate' = Remove registration mean inclinations before applying the scan
#                 mean inclinations rotations.
no_adjust = True
warp = False
mr_warp = True
tr_warp = True
mr_rotate = True

# Georeference to UTM (True) or leave in SOCS (False)
georef = True
# ------------------------------------------------------------------------------


# Only load or compute once
if mr_warp or tr_warp or mr_rotate:
    reg_it, reg_roll, reg_pitch = get_incl(reg_incl_file)
if tr_warp:
    reg_t, reg_x, reg_y, reg_z = get_pnts(reg_pnts_file)
    reg_phi = get_phi(reg_it, reg_t, reg_x, reg_y)

# Cycle through scans
laz_files = [f for f in os.listdir(data_dir) if f.endswith(".laz")]
for laz_file in laz_files:
    gc.collect()
    
    # MTA'd, unfiltered LAZ file in SOCS and corresponding inclination file
    laz_file = data_dir + "/" + laz_file
    root, _ = os.path.splitext(os.path.basename(laz_file))
    incl_file = data_dir + "/" + root + "-incl.txt"

    print("Processing {}".format(laz_file))

    # Read in point and inclination data, compute phi
    t, x, y, z = get_pnts(laz_file)
    if warp or mr_warp or tr_warp or mr_rotate:
        it, roll, pitch = get_incl(incl_file)
    if tr_warp:
        phi = get_phi(it, t, x, y)

    # ADJUSTMENT OPTIONS:
    # No point adjustment
    if no_adjust:
        no_adj(t, x, y, z,
               georef, sop_file, pop_file, data_dir, root)

    # Non-rigid warp with inclination
    if warp:
        warp_adj(t, x, y, z, it, roll, pitch, 
                 georef, sop_file, pop_file, data_dir, root)

    # Non-rigid warp after removing mean MSA inclination
    if mr_warp:
        mr_warp_adj(t, x, y, z, it, roll, pitch,
                    reg_roll, reg_pitch,
                    georef, sop_file, pop_file, data_dir, root)

    # Non-rigid warp after removing MSA cyclical trend
    if tr_warp:
        tr_warp_adj(t, x, y, z, it, phi, roll, pitch,
                    reg_phi, reg_roll, reg_pitch,
                    georef, sop_file, pop_file, data_dir, root)

    # Mean rigid rotation after removing mean MSA inclination
    if mr_rotate:
        mr_rotate_adj(t, x, y, z, it, roll, pitch,
                      reg_roll, reg_pitch,
                      georef, sop_file, pop_file, data_dir, root)