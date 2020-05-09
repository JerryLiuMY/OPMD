import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import linear_model
from analysis.tools import load_hdul, load_data
from analysis.plots import make_bars
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression
sns.set()


def correlation(file_name, C, i, j, ax, algo='RANSAC'):
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
        prediction = ransac.predict(mean_el.reshape(-1, 1))

    else:
        huber = linear_model.HuberRegressor(epsilon=1.35, max_iter=100, alpha=0.0001, fit_intercept=False)
        huber.fit(mean_el.reshape(-1, 1), corr_ij)
        outlier_mask = huber.outliers_
        inlier_mask = np.logical_not(outlier_mask)
        prediction = huber.predict(mean_el.reshape(-1, 1))

    ax.plot(mean_el[inlier_mask][2:], corr_ij[inlier_mask][2:], 'o', label=f'Channel {str(C)}, $R_{{{str(i)+str(j)}}}$')
    # ax.plot(mean_el[outlier_mask], corr_ij[outlier_mask], 'x', label='Outlier')
    # ax.plot(mean_el, prediction, '-', linewidth=4)
    ax.set_xlabel('Mean Pixel Count (el); Total Points = 400')
    ax.set_ylabel('Correlation (frac)')
    ax.legend(loc='upper left')

    return inlier_mask


def correlation_map(file_name, C, limit, ax):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    mean_el, diffvr_el, corr, gain = load_data(hdul, C)
    X, Y = np.meshgrid(np.arange(limit), np.arange(limit))

    Z = np.zeros([limit, limit])
    ij_pairs = [(i, j) for i in np.arange(limit) for j in np.arange(limit) if i + j != 0]
    for ij_pair in ij_pairs:
        i, j = ij_pair[0], ij_pair[1]
        reg = LinearRegression(fit_intercept=False).fit(np.linspace(0, 1, np.shape(corr)[0]).reshape(-1, 1), corr[:, i, j])
        Z[i, j] = reg.coef_[0]

    ax.view_init(ax.elev+15, ax.azim + 102)
    ax.set_xlabel('Parallel direction (plx)')
    ax.set_ylabel('Serial direction (plx)')
    ax.set_zlabel('Coefficient (frac)')
    make_bars(ax, X, Y, Z, width=0.23)


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
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    correlation(file_name, C, i=0, j=1, ax=ax)
    correlation(file_name, C, i=1, j=0, ax=ax)
    # photometry(file_name, C, inlier_mask)
