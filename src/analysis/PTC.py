import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from analysis.tools import load_hdul, load_data
sns.set()

file_list = ['PTC20-21-03-05-54-13.fits', 'PTC20-21-03-05-58-39.fits', 'PTC20-21-03-19-19-04.fits',
             'PTC20-21-03-19-19-05.fits', 'PTC20-21-03-19-23-06.fits']
CHANNEL_16 = np.arange(16) + 1
CHANNEL_7 = [5, 6, 10, 11, 4, 7, 13]
CHANNEL_5 = [5, 6, 7, 10, 11]


def PTC(file_name):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    for C in CHANNEL_5:
        mean_el, diffvr_el, corr, gain = load_data(hdul, C)
        channel_data = hdul[1].data[hdul[1].data['chans'] == C]
        mean, diffvr = channel_data['mn1db'], channel_data['diffvr']
        axes[0].plot(mean, diffvr, 'o', label=f'Channel {str(C)}')
        axes[1].plot(mean_el, diffvr_el, 'o', label=f'Channel {str(C)}')

    axes[0].legend(loc='upper left')
    axes[0].set_xlabel('Mean Pixel Count (DN)')
    axes[0].set_ylabel('Variance (DN$^2$)')

    lin = np.linspace(0, 70000, 5000)
    axes[1].plot(lin, lin, '--')
    axes[1].legend(loc='upper left')
    axes[1].set_xlabel('Mean Pixel Count (el)')
    axes[1].set_ylabel('Variance ($el^2$)')


def PTC_fit(file_name):
    pass

# plt.close("all")
#
# fig, ax = plt.subplots(1, 2)
#
# ax[0].plot(exps, medians, "o")
# ax[1].plot(medians, np.sqrt(diffvr), "o")
# ax[1].plot(medians, np.sqrt(vr1), "--")
#
# ax[0].set_xlabel("exposure time (s)")
# ax[0].set_ylabel("median (DN)")
# ax[1].set_xlabel("median (DN)")
# ax[1].set_ylabel("$\sigma$ (DN)")
# ax[1].loglog()
#
#
# #now let's plot some correlation coefficients
#
# correls = channel_data["correls"].reshape(400, 10, 10)
#
# plt.figure()
# plt.plot(medians, correls[:, 0, 1], "o", label="R01")
# plt.plot(medians, correls[:, 1, 0], "x", label="R10")
# plt.xlabel("median (DN)")
# plt.ylabel("R")
# plt.ylim(0, 0.08)

#as you can see, although the general trend of the correlations is as expected,
#we have many points which have been "contaminated" somehow, one thing to investigate
#is how this has happenned (e.g. do they match with images where the radiomaetry tells us)
#that there was a big difference between exposure 1 & 2 ??



