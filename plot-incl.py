import matplotlib.pyplot as plt
import numpy as np


inc104933 = np.loadtxt("180801_104933_incl.txt", delimiter=",", skiprows=1)
inc120216 = np.loadtxt("180801_120216_incl.txt", delimiter=",", skiprows=1)

fig, ax = plt.subplots()
ax.plot(inc104933[:,0], inc104933[:,1])
plt.show()

