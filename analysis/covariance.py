import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import linear_model
from sklearn.linear_model import LinearRegression, RANSACRegressor
from analysis.tools import load_hdul, load_data
from analysis.tools import poly_fit
from analysis.tools import CHANNEL_5
sns.set()


def covariance(file_name, fit, ax):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    data_len = len(load_data(hdul, 5)[0])
    mean_el_ave, cov_el_ave = np.zeros(np.shape(data_len)), np.zeros(np.shape(data_len))

    ijs = [(i, j) for i in range(0, 10) for j in range(0, 10) if i + j != 0]
    for C in CHANNEL_5:
        mean_el, cov_el, corr, gain = load_data(hdul, C)
        mean_el, cov_el = mean_el/1000, cov_el/1000
        for ij in ijs:
            i, j = ij[0], ij[1]
            if fit is True:
                reg = LinearRegression(fit_intercept=False).fit(mean_el.reshape(-1, 1), corr[:, i, j])
                corr_ij = reg.predict(mean_el.reshape(-1, 1))
                # ransac = RANSACRegressor(residual_threshold=0.01, stop_probability=0.99)
                # ransac.fit(mean_el.reshape(-1, 1), corr[:, i, j])
                # corr_ij = ransac.predict(mean_el.reshape(-1, 1))
            else:
                corr_ij = corr[:, i, j]

            cov_el = cov_el + corr_ij * mean_el

            """
            if C == 10:
                cov_el = cov_el + corr_ij * mean_el * 1.3
            else:
                cov_el = cov_el + corr_ij * mean_el * 5.2
            """

        ax.plot(mean_el, cov_el, 'o', label=f'Channel {str(C)}')
        mean_el_ave, cov_el_ave = mean_el_ave + mean_el/4, cov_el_ave + cov_el/4

    lin = np.linspace(0, 72, 5000)
    ax.plot(lin, lin, '--')
    ax.set_xlabel('Mean (kel)')
    ax.set_ylabel('Variance + Covariance ($kel^2$)')
    ax.legend(loc='upper left')
    ax.set_xlim(-2, 74)

    return mean_el_ave, cov_el_ave


def covariance_fit(mean_el_ave, cov_el_ave, deg):
    cov_el_1, cov_el_n = poly_fit(mean_el_ave, cov_el_ave, deg=deg)
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    lin = np.linspace(0, 72000, 5000)
    axes[0].plot(lin, lin, '--', label=f'Poisson')
    axes[0].plot(mean_el_ave, cov_el_ave, 'o', label=f'PTC')
    axes[1].plot(mean_el_ave, cov_el_ave - cov_el_1, 'x', label=f'deg=1')
    axes[1].plot(mean_el_ave, cov_el_ave - cov_el_n, 'x', label=f'deg={deg}')
    axes[1].legend()
