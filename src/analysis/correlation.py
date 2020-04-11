import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import linear_model
from analysis.tools import load_hdul, load_data
sns.set()


def correlation(file_name, C):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    plt.figure(figsize=(8, 6))
    mean_el, diffvr_el, corr, gain = load_data(hdul, C)
    corr_10, corr_20 = corr[:, 1, 0], corr[:, 2, 0]
    plt.plot(mean_el, corr_10, 'o', label=f'Channel {str(C)}, $R_10$')
    plt.plot(mean_el, corr_20, 'x', label=f'Channel {str(C)}, $R_20$')

    plt.legend(loc='upper left')
    plt.xlabel('Mean Pixel Count (el)')
    plt.ylabel('Correlation (frac)')


def correlation_fit(file_name, C, i=1, j=0, algo='RANSAC'):
    assert algo in ['RANSAC', 'HUBER']
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    mean_el, diffvr_el, corr, gain = load_data(hdul, C)
    corr_ij = corr[:, i, j]

    if algo == 'RANSAC':
        threshold = 0.01 if (i <= 3 and j <= 3) else 0.005
        ransac = linear_model.RANSACRegressor(residual_threshold=threshold, stop_probability=0.99)
        ransac.fit(mean_el.reshape(-1, 1), corr_ij)
        inlier_mask = ransac.inlier_mask_
        outlier_mask = np.logical_not(inlier_mask)

    else:
        huber = linear_model.HuberRegressor(epsilon=1.35, max_iter=100, alpha=0.0001, fit_intercept=False)
        huber.fit(mean_el.reshape(-1, 1), corr_ij)
        outlier_mask = huber.outliers_
        inlier_mask = np.logical_not(outlier_mask)

    fig, axes = plt.subplots(1, 2, figsize=(24, 8))
    axes[0].plot(mean_el[inlier_mask], corr_ij[inlier_mask], 'o')
    axes[0].plot(mean_el[inlier_mask], corr_ij[inlier_mask], 'x', label='Inlier')
    axes[0].plot(mean_el[outlier_mask], corr_ij[outlier_mask], 'x', label='Outlier')
    axes[0].set_xlabel('Mean Pixel Count (el); Total Points = 400')
    axes[0].set_ylabel('Correlation (frac)')
    axes[0].legend(loc='upper left')

    axes[1].plot(mean_el[inlier_mask], corr_ij[inlier_mask], 'o', label='Inlier')
    axes[1].set_xlabel(f'Mean Pixel Count (el); Remaining Points = {np.shape(mean_el[inlier_mask])[0]}')
    axes[1].set_ylabel('Correlation (frac)')
    axes[1].legend(loc='upper left')

    return inlier_mask


def photometry(file_name, C, inlier_mask):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    outlier_mask = np.logical_not(inlier_mask)

    mean_el, diffvr_el, corr, gain = load_data(hdul, C)
    channel_data = hdul[1].data[hdul[1].data['chans'] == C]
    foo = np.shape(mean_el)[0]
    mean1_el, mean2_el = channel_data['mn1db'][:foo] * gain, channel_data['mn2db'][:foo] * gain
    mean1_ph, mean2_ph = channel_data['photons1'][:foo], channel_data['photons2'][:foo]
    mean_el_diff = (mean1_el - mean2_el) / max(mean1_el - mean2_el)
    mean_ph_diff = (mean1_ph - mean2_ph) / max(mean1_ph - mean2_ph)

    print(np.shape(mean_el_diff[inlier_mask]))
    print(np.shape(mean_el_diff[outlier_mask]))

    plt.figure(figsize=(8, 6))
    plt.plot(mean_ph_diff[inlier_mask], mean_el_diff[inlier_mask], '.', label='inlier')
    plt.plot(mean_ph_diff[outlier_mask], mean_el_diff[outlier_mask], '.', label='outlier')

    plt.legend(loc='upper left')
    plt.xlabel('Normalized Photon Difference (frac)')
    plt.ylabel('Normalized Electron Difference (frac)')


def run_correlation(file_name, C):
    correlation(file_name, C)
    inlier_mask = correlation_fit(file_name, C, i=1, j=0, algo='RANSAC')
    photometry(file_name, C, inlier_mask)
