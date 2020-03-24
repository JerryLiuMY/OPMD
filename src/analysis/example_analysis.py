from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import os
from global_settings import FRAME_FOLDER

hdul = fits.open(os.path.join(FRAME_FOLDER, 'PTC20-21-03-19-19-04.fits'))

print(hdul[1].header[:20])
print(hdul[1].columns)
channel_data = hdul[1].data[hdul[1].data["chans"] == 5]
exposure_times = channel_data["exps"]
medians = channel_data["md1"]
diffvr = channel_data["diffvr"]
vr1 = channel_data["vr1"]

#print out the metadata header (which will tell us VBB and value of WIDEINT etc)
#the first few rows are metadata, the rest are column definitions

#let's do an example plot of the exposure time for channel 5 against the median
# and the exposure time against the differenced variance
#of the first of the flat pairs
#note how we select only the rows with "chans" == 5


plt.close("all")

fig, ax = plt.subplots(1, 2)

ax[0].plot(exposure_times, medians, "o")
ax[1].plot(medians, np.sqrt(diffvr), "o")
ax[1].plot(medians, np.sqrt(vr1), "--")

ax[0].set_xlabel("exposure time (s)")
ax[0].set_ylabel("median (DN)")
ax[1].set_xlabel("median (DN)")
ax[1].set_ylabel("$\sigma$ (DN)")
ax[1].loglog()


#now let's plot some correlation coefficients

correls = channel_data["correls"].reshape(400, 10, 10)

plt.figure()
plt.plot(medians, correls[:, 0, 1], "o", label="R01")
plt.plot(medians, correls[:, 1, 0], "x", label="R10")
plt.xlabel("median (DN)")
plt.ylabel("R")
plt.ylim(0, 0.08)

#as you can see, although the general trend of the correlations is as expected,
#we have many points which have been "contaminated" somehow, one thing to investigate
#is how this has happenned (e.g. do they match with images where the radiomaetry tells us)
#that there was a big difference between exposure 1 & 2 ??



