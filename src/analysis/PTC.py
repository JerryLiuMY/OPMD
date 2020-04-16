import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from analysis.tools import CHANNEL_5
from analysis.tools import load_hdul, load_data
from analysis.tools import dip_remove, poly_fit
sns.set()


def PTC(file_name):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    fig1, axes = plt.subplots(1, 2, figsize=(24, 8))
    fig2, ax = plt.subplots(1, 1, figsize=(8, 6))

    for C in CHANNEL_5:
        channel_data = hdul[1].data[hdul[1].data['chans'] == C]
        mean, diffvr = channel_data['mn1db'], channel_data['diffvr']

        mean_el, diffvr_el, corr, gain = load_data(hdul, C, cutoff=1)
        mean_el, diffvr_el = dip_remove(mean_el, diffvr_el, cutoff=0.8)

        axes[0].plot(mean, diffvr, 'o', label=f'Channel {str(C)}')
        axes[1].plot(mean_el, diffvr_el, 'o', label=f'Channel {str(C)}')
        ax.plot(mean_el, diffvr_el - mean_el, 'o', label=f'Channel {str(C)}')

    axes[0].legend(loc='upper left')
    axes[0].set_xlabel('Mean Pixel Count (DN)', fontsize=15)
    axes[0].set_ylabel('Variance (DN$^2$)', fontsize=15)

    lin = np.linspace(0, 70000, 5000)
    axes[1].plot(lin, lin, '--')
    axes[1].legend(loc='upper left')
    axes[1].set_xlabel('Mean Pixel Count (el)', fontsize=15)
    axes[1].set_ylabel('Variance ($el^2$)', fontsize=15)
    axes[1].annotate('Possion Statistics: $\sigma^2=\mu$', xy=(65000, 65000), xytext=(40000, 70000),
                     arrowprops=dict(width=2, headlength=4, facecolor='black'), fontsize=14)

    lin = np.linspace(0, 72000, 5000)
    ax.plot(lin, np.zeros(5000), '--')
    ax.legend(loc='lower left')
    ax.set_xlabel('Mean Pixel Count (el)', fontsize=11)
    ax.set_ylabel('Variance ($el^2$)', fontsize=11)
    ax.set_xlim(-2000, 72000)


def PTC_fit(file_name, deg):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    data_len = len(load_data(hdul, 5)[0])
    mean_el_ave, diffvr_el_ave = np.zeros(np.shape(data_len)), np.zeros(np.shape(data_len))

    for idx, C in enumerate(CHANNEL_5):
        mean_el, diffvr_el, corr, gain = load_data(hdul, C)
        mean_el, diffvr_el = dip_remove(mean_el, diffvr_el)
        mean_el_ave, diffvr_el_ave = mean_el_ave + mean_el, diffvr_el_ave + diffvr_el
    mean_el_ave, diffvr_el_ave = mean_el_ave/5, diffvr_el_ave/5
    diffvr_el_1, diffvr_el_n = poly_fit(mean_el_ave, diffvr_el_ave, deg)

    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    lin = np.linspace(0, 60000, 5000)
    axes[0].plot(lin, lin, '--', label=f'Poisson')
    axes[0].plot(mean_el_ave, diffvr_el_ave, 'o', label=f'PTC')
    axes[0].legend()
    axes[1].plot(mean_el_ave, diffvr_el_ave - diffvr_el_1, 'o', label=f'deg=1')
    axes[1].plot(mean_el_ave, diffvr_el_ave - diffvr_el_n, 'o', label=f'deg={deg}')
    axes[1].legend()


def run_PTC(file_name, deg=2):
    PTC(file_name)
    PTC_fit(file_name, deg=deg)
