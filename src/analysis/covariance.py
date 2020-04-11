import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import linear_model
from analysis.tools import load_hdul, load_data
sns.set()


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