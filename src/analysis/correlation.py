import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import linear_model
from analysis.tools import load_hdul, load_data
sns.set()


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