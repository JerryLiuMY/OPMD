import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import linear_model
from analysis.tools import load_hdul, load_data
from analysis.plots import make_bars
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression
import pandas as pd
sns.set()


def correlation(file_name, C, i, j, ax):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    mean_el, diffvr_el, corr, gain = load_data(hdul, C)
    mean_el = mean_el / 1000
    corr_ij = corr[:, i, j]

    # if i == 0 and j == 1:
    #     corr_ij -= 0.0008

    reg = LinearRegression(fit_intercept=True).fit((mean_el).reshape(-1, 1), corr_ij)
    prediction = reg.predict((mean_el).reshape(-1, 1))
    # ransac = linear_model.RANSACRegressor(residual_threshold=0.01, stop_probability=0.99)
    # ransac.fit(mean_el.reshape(-1, 1), corr_ij)
    # inlier_mask = ransac.inlier_mask_
    # prediction = ransac.predict(mean_el.reshape(-1, 1))
    # outlier_mask = np.logical_not(inlier_mask)
    # ax.plot(mean_el[outlier_mask], corr_ij[outlier_mask], 'x', label='Outlier')

    p = ax.scatter(mean_el[5:], corr_ij[5:], edgecolors='k', label=f'Channel average, $R_{{{str(i)+str(j)}}}$')
    ax.plot(mean_el, prediction, '-', color=p.get_facecolor()[0], linewidth=6)
    ax.set_xlabel('Mean (kel)')
    ax.set_ylabel('Correlation (frac)')
    ax.legend(loc='upper left')
    ax.set_ylim(-0.002, 0.011)

    # return inlier_mask


def correlation_map(file_name, C, limit, ax):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    mean_el, diffvr_el, corr, gain = load_data(hdul, C)
    X, Y = np.meshgrid(np.arange(limit), np.arange(limit))

    Z = np.zeros([limit, limit])
    ij_pairs = [(i, j) for i in np.arange(limit) for j in np.arange(limit) if i + j != 0]
    for ij_pair in ij_pairs:
        i, j = ij_pair[0], ij_pair[1]
        reg = LinearRegression(fit_intercept=True).fit(np.linspace(0, 1, np.shape(corr)[0]).reshape(-1, 1), corr[:, i, j])
        Z[i, j] = reg.coef_[0]

    ax.view_init(ax.elev+15, ax.azim + 102)
    ax.set_xlabel('Serial direction (plx)')
    ax.set_ylabel('Parallel direction (plx)')
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
