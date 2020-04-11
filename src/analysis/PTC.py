import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from analysis.tools import CHANNEL_5
from analysis.tools import load_hdul, load_data
from analysis.tools import inlier, poly_fit
sns.set()


def PTC(file_name):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    for C in CHANNEL_5:
        mean_el, diffvr_el, corr, gain = load_data(hdul, C, cutoff=1)
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


def PTC_fit(file_name, deg):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    mean_el, diffvr_el = np.zeros(380), np.zeros(380)
    for C in CHANNEL_5:
        mean_el_, diffvr_el_, corr, gain = load_data(hdul, C)
        mean_el, diffvr_el = mean_el + mean_el_, diffvr_el + diffvr_el_
    mean_el, diffvr_el = mean_el/5, diffvr_el/5
    mean_el, diffvr_el = inlier(mean_el, diffvr_el)
    diffvr_el_1, diffvr_el_n = poly_fit(mean_el, diffvr_el, deg)

    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    lin = np.linspace(0, 60000, 5000)
    axes[0].plot(lin, lin, '--', label=f'Poisson')
    axes[0].plot(mean_el, diffvr_el, 'o', label=f'PTC')
    axes[0].legend()
    axes[1].plot(mean_el, diffvr_el - diffvr_el_1, 'o', label=f'deg=1')
    axes[1].plot(mean_el, diffvr_el - diffvr_el_n, 'o', label=f'deg={deg}')
    axes[1].legend()


def run_PTC(file_name, deg=2):
    PTC(file_name)
    PTC_fit(file_name, deg=deg)

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

#as you can see, although the general trend of the correlations is as expected,
#we have many points which have been "contaminated" somehow, one thing to investigate
#is how this has happenned (e.g. do they match with images where the radiomaetry tells us)
#that there was a big difference between exposure 1 & 2 ??



