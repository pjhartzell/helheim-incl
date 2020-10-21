import matplotlib.pyplot as plt
from incl import *


# User entry
laz_dir = "/mnt/e/ATLAS/south_200501-200515/laz/sine"
incl_dir = "/mnt/e/ATLAS/south_200501-200515/rxp/mta"

fig, (ax1, ax2) = plt.subplots(1, 2)
laz_files = [f for f in os.listdir(laz_dir) if f.endswith(".laz")]
for laz_file in laz_files:
    # Final, filtered LAZ file in UTM
    laz_file = laz_dir + "/" + laz_file
    print(laz_file)

    # Corresponding file of inclination roll and pitch in degrees
    root, ext = os.path.splitext(os.path.basename(laz_file))
    incl_file = incl_dir + "/" + root + "-incl.txt"

    # Read in the point and inclination data
    pt, x, y, z = get_socs(laz_file)
    it, roll, pitch = get_incl(incl_file)

    # Filter inclination data
    filtered_roll = filter_incl(roll, 801)
    filtered_pitch = filter_incl(pitch, 801)

    # ax1.plot(pt)
    # ax2.plot(it)
    # plt.show()

    # Get phi for each inclination time
    phi = get_phi(it, pt, x, y)

    # Plot
    ax1.plot(phi, filtered_roll)
    ax2.plot(phi, filtered_pitch)

ax1.set_title("Roll")
ax2.set_title("Pitch")
ax1.set_xlabel("Phi (deg)")
ax2.set_xlabel("Phi (deg)")
ax1.set_ylabel("Inclination (deg)")
ax2.set_ylabel("Inclination (deg)")
plt.show()