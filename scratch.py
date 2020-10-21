import numpy as np
import matplotlib.pyplot as plt
from incl import *


incl_file = "/mnt/e/ATLAS/registration_scans/south/190804_202537-incl.txt"

it, roll, pitch = get_incl(incl_file)
# filtered_roll = filter_incl(roll, 71)
# filtered_pitch = filter_incl(pitch, 71)

fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.plot(it, roll, 'b')
# ax1.plot(it, filtered_roll, 'r')
ax2.plot(it, pitch, 'b')
# ax2.plot(it, filtered_pitch, 'r')
ax1.set_title("Roll")
ax2.set_title("Pitch")
ax1.set_xlabel("Time (s)")
ax2.set_xlabel("Time (s)")
ax1.set_ylabel("Inclination (deg)")
ax2.set_ylabel("Inclination (deg)")
plt.show()

