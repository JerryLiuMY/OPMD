import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import linear_model
from analysis.tools import load_hdul, load_data
from analysis.tools import dip_remove, poly_fit
from analysis.tools import CHANNEL_5
sns.set()


def covariance(file_name, algo='RANSAC', fit=True):
    assert algo in ['RANSAC', 'HUBER']
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    plt.figure(figsize=(8, 6))
    data_len = len(load_data(hdul, 5)[0])
    mean_el_ave, cov_el_ave = np.zeros(np.shape(data_len)), np.zeros(np.shape(data_len))

    ij_pairs = [(i, j) for i in range(0, 8) for j in range(0, 8) if i + j != 0]
    for C in CHANNEL_5:
        mean_el, diffvr_el, corr, gain = load_data(hdul, C)
        mean_el, cov_el = dip_remove(mean_el, diffvr_el, cutoff=0.8)
        for ij_pair in ij_pairs:
            i, j = ij_pair[0], ij_pair[1]
            threshold = 0.01 if (i <= 3 and j <= 3) else 0.005
            if fit is True and algo == 'RANSAC':
                ransac = linear_model.RANSACRegressor(residual_threshold=threshold, stop_probability=0.99)
                ransac.fit(mean_el.reshape(-1, 1), corr[:, i, j])
                corr_ij = ransac.predict(mean_el.reshape(-1, 1))
            elif fit is True and algo == 'HUBER':
                huber = linear_model.HuberRegressor(epsilon=1.35, max_iter=100, alpha=0.1, fit_intercept=False)
                huber.fit(mean_el.reshape(-1, 1), corr[:, i, j])
                corr_ij = huber.predict(mean_el.reshape(-1, 1))
            else:
                corr_ij = corr[:, i, j]
            cov_el = cov_el + corr_ij * mean_el

        mean_el_ave, cov_el_ave = mean_el_ave + mean_el, cov_el_ave + cov_el
        plt.plot(mean_el, cov_el, 'o', label=f'Channel {str(C)}')

    mean_el_ave, cov_el_ave = mean_el_ave/5, cov_el_ave/5
    lin = np.linspace(0, 70000, 5000)
    plt.plot(lin, lin, '--')
    plt.xlabel('Mean Pixel Count (el)')
    plt.ylabel('Variance + Covariance ($el^2$)')
    plt.legend(loc='upper left')

    return mean_el_ave, cov_el_ave


def covariance_fit(mean_el_ave, cov_el_ave, deg):
    cov_el_1, cov_el_n = poly_fit(mean_el_ave, cov_el_ave, deg=deg)
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    lin = np.linspace(0, 60000, 5000)
    axes[0].plot(lin, lin, '--', label=f'Poisson')
    axes[0].plot(mean_el_ave, cov_el_ave, 'o', label=f'PTC')
    axes[1].plot(mean_el_ave, cov_el_ave - cov_el_1, 'o', label=f'deg=1')
    axes[1].plot(mean_el_ave, cov_el_ave - cov_el_n, 'o', label=f'deg={deg}')
    axes[1].legend()


def run_covariance(file_name):
    mean_el_ave, cov_el_ave = covariance(file_name, algo='RANSAC', fit=True)
    covariance_fit(mean_el_ave, cov_el_ave, deg=3)


def calculate_correlation_coeffs(dat, nx=10, ny=10):
    out = np.zeros((nx, ny))
    s = np.sum(dat**2)
    for i in range(nx):
        for j in range(ny):
            out[i, j] = np.sum(np.roll(dat, (i, j), (0, 1)) * dat) / s
    return out
