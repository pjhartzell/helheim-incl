import matplotlib.pyplot as plt
from incl import *


# User entry
laz_dir = "/mnt/e/ATLAS/south_200501-200515/laz/test"
incl_dir = "/mnt/e/ATLAS/south_200501-200515/rxp/mta"
plot_incl = True

# The work
laz_files = [f for f in os.listdir(laz_dir) if f.endswith(".laz")]
for laz_file in laz_files:
    # Final, filtered LAZ file in UTM
    laz_file = laz_dir + "/" + laz_file
    print("Applying inclination to {}".format(laz_file))

    # Corresponding file of inclination roll and pitch in degrees
    root, ext = os.path.splitext(os.path.basename(laz_file))
    incl_file = incl_dir + "/" + root + "-incl.txt"

    # Read in the point and inclination data
    pt, x, y, z = get_socs(laz_file)
    it, roll, pitch = get_incl(incl_file)

    # Filter the inclination data to remove high frequency components
    filtered_roll = filter_incl(roll, 101)
    filtered_pitch = filter_incl(pitch, 101)

    #  Plot raw and filtered inclination data, if desired
    if plot_incl:
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot(roll, 'b', label='Raw')
        ax1.plot(filtered_roll, 'r', label='Filtered')
        ax1.set_xlabel('time (s)')
        ax1.set_ylabel('inclination (deg)')
        ax1.set_title('Roll')
        ax2.plot(pitch, 'b')
        ax2.plot(filtered_pitch, 'r')
        ax2.set_xlabel('time (s)')
        ax2.set_ylabel('inclination (deg)')
        ax2.set_title('Pitch')
        ax1.legend()
        plt.show()

    # Apply filtered inclination to point data in SOCS frame
    xr, yr, zr = apply_incl(pt, x, y, z, it, filtered_roll, filtered_pitch)

    # Save the corrected SOCS point data
    root, ext = os.path.splitext(laz_file)
    outfilename = root + "-socs-incl_applied" + ext
    save_socs(outfilename, pt, xr, yr, zr)