from astropy.io import fits
import os
import matplotlib.pyplot as plt
import numpy as np
from global_settings import EXPERIMENT_FOLDER
import seaborn as sns
from sklearn import linear_model
sns.set()

FRAME_FOLDER = os.path.join(EXPERIMENT_FOLDER, 'frames')
file_list = ['PTC20-21-03-05-54-13.fits', 'PTC20-21-03-05-58-39.fits', 'PTC20-21-03-19-19-04.fits',
             'PTC20-21-03-19-19-05.fits', 'PTC20-21-03-19-23-06.fits']
CHANNEL_16 = np.arange(16) + 1
CHANNEL_7 = [5, 6, 10, 11, 4, 7, 13]
CHANNEL_5 = [5, 6, 7, 10, 11]


def load_hdul(file_name):
    hdul = fits.open(os.path.join(FRAME_FOLDER, file_name))
    vbb, wideint = hdul[1].header['VBB'], hdul[1].header['WIDEINT']
    wwideint = hdul[1].header['WWIDEINT'] if 'WWIDEINT' in hdul[1].header else None

    return hdul, vbb, wideint, wwideint


def load_data(hdul, C):
    channel_data = hdul[1].data[hdul[1].data['chans'] == C]
    mean = channel_data['mn1db']
    diffvr = channel_data['diffvr']
    corr = channel_data['correls'].reshape(400, 10, 10)
    gain = (channel_data['mn1db'][11] - channel_data['mn1db'][1]) / (channel_data['diffvr'][11] - channel_data['diffvr'][1])
    mean_el, diffvr_el = mean * gain, diffvr * (gain ** 2)

    return mean_el, diffvr_el, corr, gain


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


def correlation(file_name):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    plt.figure(figsize=(8, 6))
    for C in [5, 6]:
        mean_el, diffvr_el, corr, gain = load_data(hdul, C)
        corr_10, corr_20 = corr[:, 1, 0], corr[:, 2, 0]
        plt.plot(mean_el, corr_10, 'o', label=f'Channel {str(C)}, $R_10$')
        plt.plot(mean_el, corr_20, 'x', label=f'Channel {str(C)}, $R_20$')

    plt.legend(loc='upper left')
    plt.xlabel('Mean Pixel Count (el)')
    plt.ylabel('Correlation (frac)')


def photometry(file_name):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))

    for C in [5, 6]:
        mean_el, diffvr_el, corr, gain = load_data(hdul, C)
        channel_data = hdul[1].data[hdul[1].data['chans'] == C]
        mean1_el, mean2_el = channel_data['mn1db'] * gain, channel_data['mn2db'] * gain
        mean1_ph, mean2_ph = channel_data['photons1'], channel_data['photons2']
        axes[0].plot(mean_el, (mean1_el - mean2_el) / max(mean1_el - mean2_el), '.', label=f'Channel {str(C)}, mn1db-mn2db')
        axes[0].plot(mean_el, (mean1_ph - mean2_ph) / max(mean1_ph - mean2_ph), '^', label=f'Channel {str(C)}, photons1-photons2')
        axes[1].plot((mean1_el - mean2_el) / max(mean1_el - mean2_el), (mean1_ph - mean2_ph) / max(mean1_ph - mean2_ph), '.')

    axes[0].legend(loc='upper left')
    axes[0].set_xlabel('Mean Pixel Count (el)')
    axes[0].set_ylabel('Normalized Electron / Photon Difference (frac)')
    axes[1].set_xlabel('Normalized Electron Difference (frac)')
    axes[1].set_ylabel('Normalized Photon Difference (frac)')


def correlation_fit(file_name, C, algo='RANSAC'):
    assert algo in ['RANSAC', 'HUBER']
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    mean_el, diffvr_el, corr, gain = load_data(hdul, C)
    corr_10 = corr[:, 1, 0]

    if algo == 'RANSAC':
        ransac = linear_model.RANSACRegressor(stop_probability=0.99)
        ransac.fit(mean_el.reshape(-1, 1), corr_10)
        inlier_mask = ransac.inlier_mask_
        outlier_mask = np.logical_not(inlier_mask)

    else:
        huber = linear_model.HuberRegressor(epsilon=1.35, max_iter=100, alpha=0.0001)
        huber.fit(mean_el.reshape(-1, 1), corr_10)
        outlier_mask = huber.outliers_
        inlier_mask = np.logical_not(outlier_mask)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    axes[0].plot(mean_el[inlier_mask], corr_10[inlier_mask], 'o')
    axes[0].plot(mean_el[inlier_mask], corr_10[inlier_mask], 'x', label='Inlier')
    axes[0].plot(mean_el[outlier_mask], corr_10[outlier_mask], 'x', label='Outlier')
    axes[0].set_xlabel('Mean Pixel Count (el); Total Points = 400')
    axes[0].set_ylabel('Correlation (frac)')
    axes[0].legend(loc='upper left')

    axes[1].plot(mean_el[inlier_mask], corr_10[inlier_mask], 'o', label='Inlier')
    axes[1].set_xlabel(f'Mean Pixel Count (el); Remaining Points = {np.shape(mean_el[inlier_mask])[0]}')
    axes[1].set_ylabel('Correlation (frac)')
    axes[1].legend(loc='upper left')


def covariance(file_name, C, algo='RANSAC', fit=True):
    assert algo in ['RANSAC', 'HUBER']
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    mean_el, diffvr_el, corr, gain = load_data(hdul, C)

    cov_el = diffvr_el
    ij_pairs = [(i, j) for i in range(0, 10) for j in range(0, 10) if i + j != 0]
    for ij_pair in ij_pairs:
        i, j = ij_pair[0], ij_pair[1]
        if i + j != 0:
            if fit is True and algo == 'RANSAC':
                ransac = linear_model.RANSACRegressor(stop_probability=0.99)
                ransac.fit(mean_el.reshape(-1, 1), corr[:, i, j])
                corr_ij = ransac.predict(mean_el.reshape(-1, 1))
            elif fit is True and algo == 'HUBER':
                huber = linear_model.HuberRegressor(epsilon=1.35, max_iter=100, alpha=0.0001)
                huber.fit(mean_el.reshape(-1, 1), corr[:, i, j])
                corr_ij = huber.predict(mean_el.reshape(-1, 1))
            else:
                corr_ij = corr[:, i, j]
            cov_el = cov_el + corr_ij * diffvr_el

    plt.figure(figsize=(8, 6))
    lin = np.linspace(0, 70000, 5000)
    plt.plot(lin, lin, '--')
    plt.plot(mean_el, cov_el, 'o', label='Variance + Covariance')
    plt.plot(mean_el, diffvr_el, 'o', label='Variance')
    plt.xlabel('Mean Pixel Count (el)')
    plt.ylabel('Variance + Covariance ($el^2$)')
    plt.legend(loc='upper left')

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



